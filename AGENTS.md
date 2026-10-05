# Codex working agreement for Veto

Read `README.md`, `PRODUCT_SPEC.md`, `SAFETY_POLICY.md`, and the current milestone in `IMPLEMENTATION_PLAN.md` before changing code. Treat `HACKATHON_RULES_AND_SOURCES.md` as a snapshot that must be rechecked against official pages when a fact might change. Record decisions and evidence in `DECISIONS_AND_PROGRESS.md`.

## Mission and boundaries

- Build an original Windows personal AI agent for the **Personal AI** track. Use a real NVIDIA open model on Nebius Token Factory at runtime. Keep the model/provider configurable so the owner can change it after the event.
- Implement the **current milestone only** unless a dependency is essential for its acceptance check. At the end, report the behavior delivered, files changed, commands/tests run, evidence, and the next milestone.
- Explain new concepts for a beginner in one or two plain sentences. Provide exact Windows PowerShell commands and expected outcomes. Never imply a command was run if it was not.
- Prefer deterministic adapters and a small fixed tool registry. A language model may *propose* a tool call; code validates scope, arguments, and approval before execution. Never execute model-generated code, raw shell, arbitrary URLs, or arbitrary registry edits.
- Use a native Windows process for actual Windows file and settings actions. WSL can assist development but cannot be assumed to operate Windows UI reliably.
- The owner requested a **“Hey Veto”** wake word. Implement it as a user-enabled local listener with a visible microphone indicator and immediate mute/off control. Do not install a startup service or enable always-listening on first launch without the owner's explicit action in the app. Never open a remote-control server or non-loopback listener without separate authorization.
- Keep real user files, email, messages, credentials, and screenshots out of the public repo, demo, logs, tests, and prompts. Use fixture data until each safe acceptance check passes.
- Give Veto a calm, capable, lightly witty personality defined in `PRODUCT_SPEC.md`. Write original lines and use an original or properly licensed voice; do not imitate an actor's voice or copy dialogue from a film.

## Source and truth rules

- For Nebius endpoints, available NVIDIA model IDs, pricing, credits, third-party APIs, and contest rules, consult current official documentation or the logged-in account. Put exact source URL and checked date in `DECISIONS_AND_PROGRESS.md`. If unable to verify, label it **unverified** and avoid encoding a guess as fact.
- The active code and real test output outrank planning claims. If docs and runtime disagree, reproduce the result, fix the docs, and record the decision.
- Do not claim voice, background work, email sending, hosted access, or screen automation works until its acceptance check has passed on the target machine.
- Cite or link borrowed libraries/assets and verify their licenses. A README badge alone is insufficient proof of a license.

## Safety gates

`SAFETY_POLICY.md` is a non-negotiable implementation requirement. Before any filesystem mutation, the user must select the allowed folder and approve an exact plan. Check resolved paths and symlinks again at execution time. Never delete, overwrite, run shell, or send a message based solely on a model response. Implement undo for file moves. Bind the local API to `127.0.0.1` unless a later authorized design explicitly requires remote access.

Before a wider PC action, get the user's approval through **Veto's own action preview**. Do not ask the developer-user to approve every ordinary code edit in chat. Use the app permission mechanism for runtime actions.

## Milestone workflow

1. Check the working tree and read progress. Keep prior passing behavior intact.
2. State the current milestone and measurable acceptance checks.
3. Implement a thin end-to-end slice. Keep model and OS actions behind interfaces with testable fake adapters.
4. Run relevant tests and one manual end-to-end check. Avoid tests that only copy implementation behavior.
5. Update README/setup, progress, decisions, and any changed assumptions. Make a git commit when the gate passes.
6. Tell the owner exactly what to click/type to verify; stop before the next milestone.

## Git workflow preference (owner request, 5 October 2026)

- Use multiple focused commits for meaningful implementation and documentation changes; do not create empty commits just to increase the count.
- The owner requested GitHub pushes to `https://github.com/ShaileshSethi/VETO.git`. The configured `origin` uses this URL and the published branch is `main`.
- Inspect status and staged files before committing/pushing. Keep `.env`, local database/data, evidence screenshots and installed/build dependencies excluded. Never force-push or overwrite existing remote history to resolve a conflict.
- Record what actually shipped and preserve the pending live NVIDIA gate. Mock-mode commits are development evidence, not live-inference qualification.

## If blocked

Report the exact blocker and its effect. Continue with independent work. Do not fake a passed test, change the required NVIDIA/Nebius runtime into another provider, silently weaken a safety rule, or leave a purported working demo that only replays canned responses. If a key or sign-in is needed, give local setup steps; never request the secret value in chat.
