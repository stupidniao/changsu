# Agent Guidelines

## Change Workflow

All repository changes must be made on a new branch and merged into `main` through a pull request.

## Branch And PR Naming

When creating a branch or pull request, use concise, searchable names that describe the user-visible change or engineering intent.

- Branch names should use lowercase kebab-case with a type prefix: `feat/add-bill-summary`, `fix/handle-empty-drink-list`, `chore/update-bazel-config`.
- Prefer these prefixes: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`.
- If an issue or ticket id exists, include it after the prefix: `feat/CS-123-add-running-stats`.
- Avoid vague names such as `update`, `changes`, `wip`, `cursor-fix`, `my-branch`, or names based only on a person.
- PR titles should be short imperative summaries, preferably in Conventional Commit style: `feat: add bill summary`, `fix: handle empty drink list`.
- Keep branch names stable after publishing unless the user explicitly asks to rename them.
