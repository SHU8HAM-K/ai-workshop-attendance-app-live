"""Use cases: start and finish a sign-in, resolve a session.

``sign_in`` is the one door into the user table. OAuth providers reach it
through ``complete``; a password, magic link or OTP method added later builds
its own ``ExternalIdentity`` and calls ``sign_in`` directly."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from myapp.domain.exceptions import AuthenticationError, NotFoundError
from myapp.domain.user import ExternalIdentity, Identity, User
from myapp.ports.auth import IdentityProvider, SessionTokens
from myapp.ports.unit_of_work import UnitOfWork


class AuthService:
    def __init__(
        self,
        uow: UnitOfWork,
        providers: Mapping[str, IdentityProvider],
        sessions: SessionTokens,
        *,
        allowed_domains: frozenset[str] = frozenset(),
    ) -> None:
        self._uow = uow
        self._providers = providers
        self._sessions = sessions
        # Empty = anyone the provider vouches for may sign in.
        self._allowed_domains = allowed_domains

    def provider_names(self) -> list[str]:
        return list(self._providers)

    async def start(self, provider: str, *, redirect_uri: str, state: str) -> str:
        return await self._provider(provider).authorization_url(
            redirect_uri=redirect_uri, state=state
        )

    async def complete(
        self, provider: str, code: str, *, redirect_uri: str, now: datetime
    ) -> tuple[User, str]:
        """The user and a session token for the cookie."""
        identity = await self._provider(provider).exchange_code(code, redirect_uri=redirect_uri)
        user = await self.sign_in(identity, now)
        return user, self._sessions.issue(user.id)

    async def sign_in(self, identity: ExternalIdentity, now: datetime) -> User:
        """Find the user this identity belongs to, creating one on first sight.

        A new identity joins an existing user only when the provider verified
        the email; otherwise anyone could claim an address and take an account.
        """
        domain = identity.email.rpartition("@")[2].lower()
        if self._allowed_domains and domain not in self._allowed_domains:
            raise AuthenticationError(f"{identity.email} is not at an allowed domain")
        async with self._uow as uow:
            user = await uow.users.get_by_identity(identity.provider, identity.subject)
            if user is not None:
                return user
            if identity.email_verified:
                user = await uow.users.get_by_email(identity.email)
            if user is None:
                user = User.register(identity, now)
                await uow.users.add(user)
                await uow.flush()
            await uow.users.link(
                Identity(identity.provider, identity.subject, user_id=user.id, created_at=now)
            )
            await uow.commit()
            return user

    async def current_user(self, token: str | None) -> User:
        user_id = self._sessions.read(token) if token else None
        user = None
        if user_id is not None:
            async with self._uow as uow:
                user = await uow.users.get(user_id)
        if user is None:
            raise AuthenticationError("not signed in")
        return user

    def _provider(self, name: str) -> IdentityProvider:
        try:
            return self._providers[name]
        except KeyError:
            raise NotFoundError(f"unknown sign-in provider {name!r}") from None
