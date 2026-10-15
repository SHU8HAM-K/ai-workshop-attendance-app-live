import { Navigate } from "react-router";
import { loginUrl, useMe, useProviders } from "./queries";

const LABELS: Record<string, string> = {
  google: "Continue with Google",
  dev: "Sign in as the dev user",
};

/** One button per provider the API has switched on. Plain links, not fetch:
 *  the browser must follow the redirect to the provider's consent screen. */
export function LoginPage() {
  const me = useMe();
  const providers = useProviders();
  if (me.isSuccess) return <Navigate to="/" replace />;
  return (
    <div className="flex min-h-full flex-col items-center justify-center gap-6 bg-slate-50 px-6 text-center text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Sign in to MyApp</h1>
        <p className="mt-1 text-sm text-slate-500">Use an account you already have.</p>
      </div>
      <div className="flex w-full max-w-xs flex-col gap-2">
        {providers.data?.map((p) => (
          <a
            key={p}
            href={loginUrl(p)}
            className="flex h-10 items-center justify-center rounded-md border border-slate-300 text-sm transition-colors hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
          >
            {LABELS[p] ?? `Continue with ${p}`}
          </a>
        ))}
        {providers.data?.length === 0 && <p className="text-sm text-slate-500">No sign-in method is configured.</p>}
      </div>
    </div>
  );
}
