---
name: schoolnet-frontend
description: Create or update Schoolnet-branded web interfaces using the project's clean cloud-console visual language. Use for Schoolnet landing pages, dashboards, admin tables, portals, and responsive frontend components; do not use for backend-only work or unrelated brands.
---

# Schoolnet Frontend

Build polished, usable Schoolnet interfaces that feel consistent with the existing project rather than producing a generic template.

## Start With the Project

- Inspect the existing frontend, repository guidance, assets, and current changes before editing.
- Preserve the framework, build system, established components, and user-owned changes.
- Reuse existing Schoolnet logos and brand assets when present. Do not invent an official logo or claim that a placeholder mark is official.
- Keep small static experiences buildless unless the repository or requested behavior calls for a framework.

## Visual Direction

Use a restrained education-technology and cloud-console aesthetic:

- Favor white surfaces, pale gray page backgrounds, fine `#dadce0` borders, and subtle shadows.
- Use `#1a73e8` for primary actions, `#5f6368` for secondary text, `#188038` for success, and purple links around `#681da8` when reproducing console-style tables.
- Prefer Arial, Helvetica, or the project's existing sans-serif. Maintain strong readability rather than adding decorative fonts.
- Use compact, clearly labeled tables with light gray headers, generous horizontal spacing, visible row separators, and horizontal scrolling on narrow screens.
- Keep cards lightly rounded, spacing consistent, and decoration secondary to the content.
- A Schoolnet page should feel confident, modern, and practical for educators or administrators—not playful, crowded, or heavily animated.

Treat these colors and patterns as defaults, not a reason to override explicit user requirements or an established design system.

## Implementation

- Use semantic HTML landmarks and a logical heading hierarchy.
- Centralize repeated colors and spacing in CSS custom properties or the project's theme tokens.
- Make layouts responsive from 320px upward. Tables may scroll horizontally; primary content must remain readable without page-level horizontal overflow.
- Give interactive elements visible hover and keyboard-focus states. Use native controls where possible and label icon-only buttons.
- Respect `prefers-reduced-motion`; animations should be brief and nonessential.
- Implement only interactions the request needs. Do not present inert controls as working features; remove them, connect them, or clearly mark them as illustrative.
- Avoid new dependencies for styling or icons when CSS and small inline SVGs are sufficient.

## Content

- Use concise, professional language suited to education, workshops, learning platforms, and operations.
- Keep names, dates, regions, runtimes, and statuses internally consistent.
- Use realistic sample content only when the user has not supplied data, and make it clear through context that it is demonstrative.

## Validate

After implementation:

1. Run the repository's relevant build or checks when available.
2. Serve static pages locally and verify a successful HTTP response.
3. Check desktop and narrow-screen behavior when preview tooling is available.
4. Confirm links, buttons, table overflow, focus visibility, page title, and description.
5. Report what changed, what was verified, and any preview limitation.
