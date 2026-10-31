## [frontend-post-mvp] Responsive jobs repository improvements
- Codebase/domain discoveries: The frontend is a single React entrypoint with environment-based API URL configuration; jobs are currently fetched as one collection.
- Wrong assumptions and corrections: Root-level npm commands do not apply because the frontend owns its package.json; repository format-check currently reports pre-existing backend formatting drift.
- Debugging dead-ends and what actually worked: Running npm scripts from `frontend/` passed; a small pure pagination utility made focused behavior tests possible without adding a component-testing dependency.
- Techniques/patterns worth reusing: Keep pagination metadata in a pure helper and use semantic pagination navigation with live page status.
- Learnings consumed: [(none)]
