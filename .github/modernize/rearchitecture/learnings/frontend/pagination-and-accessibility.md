# Pagination and Accessibility

The frontend jobs repository uses a pure pagination helper and semantic controls so responsive and keyboard behavior can be tested without adding a UI test dependency.

## What Happened
The existing jobs screen rendered every result and had limited mobile navigation and focus affordances. A clamped `paginateItems` helper now provides stable page metadata, while the jobs screen and shell expose accessible navigation, focus-visible outlines, and a responsive horizontal navigation layout.

## Takeaway
Prefer small pure UI state helpers for deterministic tests, and pair interactive controls with visible focus states, disabled states, and `aria-live` updates.

## History
- 2026-10-26 (NextHire/frontend-post-mvp): initial
