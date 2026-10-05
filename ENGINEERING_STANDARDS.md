# Veto engineering standards

These standards make the implementation understandable and verifiable. They do not guarantee a judging score; the live NVIDIA gate and later milestone evidence still matter.

## Code and comments

- Keep API transport, UI components, inference providers and file authority separate. Name functions after their behavior and give each module one clear responsibility.
- Use strict TypeScript, parameterized SQL, bounded input and explicit errors. Store cloud credentials only on the backend. Never log prompts, credentials or personal file contents.
- Add docstrings to safety-sensitive operations and comments explaining why a check, ordering constraint or boundary exists. Avoid comments that merely repeat the code, stale claims and commented-out code.
- Format Python with Ruff and the interface with Biome. Fix lint failures instead of applying blanket suppressions. Keep runtime and development dependencies reproducible with lockfiles and exact tool versions.
- Preserve approval hashes, execution rechecks, no-overwrite Windows moves and journalled undo. Mock replies cannot authorize actions; no failed live request may silently become a mock success.

## Review and verification

Run the checks from the project directory in PowerShell:

```powershell
# First time only; installs development tools in the project environment.
.\check-veto.ps1 -Install
# Before a commit, or after editing code:
.\check-veto.ps1
```

The script stops at the first failure and checks Python lint/formatting, Windows sample safety tests, TypeScript, interface lint/formatting and production build. Tests use temporary generated fixtures and mock HTTP transports; they require no API key. GitHub Actions runs the same script on Windows for pushes and pull requests. A workflow's presence is not evidence that its remote run passed; inspect the actual Actions result.

To format edits, run `.venv\Scripts\python.exe -m ruff format backend scripts tests` from the project directory and `npm.cmd run format` inside `frontend`. Review formatting fixes and rerun checks before committing.

Use tests for observable safety outcomes: denied paths, stale approvals, collisions, stop, partial failure, crash receipts, restart persistence and restored bytes. For UI edits, also try the relevant workflow in a real browser. Record actual commands/results and limitations in `DECISIONS_AND_PROGRESS.md`; never turn an untested claim into a completed milestone.

## Current limits

This checkpoint uses generated samples and deterministic sorting. It is not a hardened personal-file manager: hostile concurrent filesystem replacement still needs further design. Live NVIDIA/Nebius account access, inference and qualification evidence are pending. Voice and wider Windows actions remain off.

Tool configuration references checked 5 October 2026: [Ruff configuration](https://docs.astral.sh/ruff/configuration/) and [Biome getting started](https://biomejs.dev/guides/getting-started/). Installed license files were inspected; see `THIRD_PARTY_NOTICES.md`.
