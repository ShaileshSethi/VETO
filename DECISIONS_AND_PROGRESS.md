# Decisions and progress log

Codex and the owner update this file after every working session. Record facts, not optimism. Do not include secrets or personal file paths.

## Current status

- **Date:** 5 October 2026
- **Phase:** explicit mock mode and sample-only file/memory workflow implemented and tested; live NVIDIA testing pending
- **Current milestone:** sample M2 development authorized while M1 live acceptance remains incomplete
- **Next exact task:** launch `run-veto.ps1 -Mode mock` and try permission → preview → approve → restart → undo on generated samples.
- **Actual focused hours:** approximately 0.5 agent hours across two sessions; owner time not measured
- **Last verified working commit:** none

## Decisions

| ID | Date | Choice | Evidence/source | Revisit trigger |
| --- | --- | --- | --- | --- |
| D01 | Oct 4 | Windows first, local runtime and sample folder | User wants safe control of their Windows laptop | If target machine differs |
| D02 | Oct 4 | Nemotron via Nebius at runtime | [Official rules](https://nebiusglobalaihackathon.devpost.com/rules) | Verify exact model ID and endpoint in account |
| D03 | Oct 4 | Fixed tools, selected roots, preview/approval, undo | PC safety requirement | Tests reveal gap |
| D04 | Oct 4 | Name **Veto**; user-enabled local “Hey Veto” wake word, push-to-talk/keyboard fallback, spoken replies, distinct calm/witty personality | Explicit owner preference | Measure accuracy/CPU on target laptop at M4 |
| D05 | Oct 4 | Original project; Blinky as reference only | [Blinky repository](https://github.com/KingSahil/Blinky) and unverified license metadata | License confirmed and explicit reuse decision |
| D06 | Oct 5 | Default candidate `nvidia/Nemotron-3_5-Lightning`; configurable, no fallback; query account `/models` before inference | https://nebius.com/services/token-factory/models/nvidia-nemotron-models-inference — public endpoint and exact ID verified Oct 5; account access not yet verified | Account catalog lacks ID or live responses fail |
| D07 | Oct 5 | Base URL `https://api.tokenfactory.nebius.com/v1/`; HTTPX OpenAI-compatible text requests | https://docs.tokenfactory.nebius.com/quickstart — verified Oct 5 | Official endpoint changes |
| D08 | Oct 5 | React static build served by FastAPI on `127.0.0.1:8765`; no separate dev server | Browser smoke check and Windows connection table show loopback only | Desktop packaging milestone |
| D09 | Oct 5 | MIT for original source; direct dependency license files inspected | LICENSE and THIRD_PARTY_NOTICES.md; Python and npm lockfiles | Distribution at M5 |
| D10 | Oct 5 | No tool execution in M1 slice; no folder permission or file content transmission | API exposes status/text chat only; tests deny action endpoint | M2 policy implementation and fixture safety tests |
| D11 | Oct 5 | Explicit mock mode while credits are pending; user-authorized sample M2 development before M1 live gate | Owner's direct request in this chat supersedes original milestone sequencing and no-mock development restriction | Credits arrive; perform live NVIDIA gate |
| D12 | Oct 5 | One fixed generated root only; metadata/local deterministic sorting; hashed exact approvals, Windows no-overwrite move and journalled undo | 48 passing tests and actual browser sort/restart/undo with byte checks | Personal-folder proposal requires further review/hardening |
| D13 | Oct 5 | SQLite schema v1 persists preferences, sample permissions and receipts; generator preserves relocated samples on restart | Real process restart retained Notes preference, permissions, 4 receipts and undo | Schema migration or packaging |

## Milestone gates

- [ ] M0 Accounts, credits, new repo, sample folder
- [ ] M1 Real NVIDIA/Nebius model call in working UI
- [ ] M2 File preview/move/undo and persistent memory, denied-path tests
- [x] Sample-only mock development gate: permissions, deterministic sorting preview/approval, real moves/undo, local preference persistence (does not complete live M1 or authorize personal data)
- [ ] M3 Bounded multi-step workflow and supported Windows action
- [ ] M4 “Hey Veto,” spoken reply, saved skill, bounded scheduled check, message draft
- [ ] M5 Windows test build, safe judge demo, 30 cases, user trials
- [ ] M6 Public repo, README, license, video, feedback, final Devpost submission

## Session template (copy below each time)

### 2026-10-05 — Explicit mock mode and sample M2 development

- **Authorization:** owner says credits arrive in a few days and requests labelled sample replies plus fixture permissions/sorting/approval/undo/preferences. This is a development exception to the earlier sequence, not an alternative hackathon runtime.
- **Time/environment:** approximately 15 minutes agent work in this session; same native Windows tools/dependencies, no new packages. This is an estimate of elapsed agent work, not measured owner focus time.
- **Behavior:** default `VETO_MODE=mock` gives fixed replies with explicit labels and no catalog/inference request; `-Mode nebius` retains real integration and never falls back to mock on failure. Both UI and API report live testing pending. Voice stays off.
- **Implementation:** added `backend/files.py`, expanded API and React UI, mock provider/settings, sample restart protection, run-script mode override, `tests/test_files.py`, README and architecture/plan notes. SQLite v1 in ignored data holds preference CRUD/export, sample grant/revocation, exact hashed plans, approval hashes, per-step identities/receipts and crash reconciliation. No arbitrary root or model-generated filesystem commands.
- **Actual checks:** `.venv/Scripts/python.exe -m pytest -q` — **48 passed, 1 deprecation warning, 5.12 seconds**; `npm.cmd run build` — TypeScript + production build passed (28 modules); pip check passed. Existing 15 tests preserved. Sandbox temp-directory and Vite subprocess restrictions required permitted reruns. One build command initially used the project root instead of frontend; corrected working directory passed.
- **Safety evidence:** denied root IDs/arbitrary extra args, relative/absolute/UNC/traversal/ADS/device names, wrong hash/no token, case-insensitive collision, changed/replaced file, revoked/regranted roots, destination junction inserted after approval and root junction at grant. No overwrite. Stop and revocation between steps leave accurate partial receipts; retry returns outcomes without a duplicate. Undo refuses occupied original paths or altered/replaced destinations. Limits and malicious filenames checked. Mock test forbids HTTP client construction even with a dummy key.
- **Browser/manual evidence:** mock question returned explicitly labelled sample reply. Initially no grant/files; selected and allowed only Veto Demo Inbox. Saved study/Notes preference, previewed **4 moves, 327 bytes**, approved and observed done receipts. Independent filesystem check confirmed exact original bytes at approved destinations and unknown-file unchanged. Stopped server, relaunched via script; generator created **0 duplicates**, Notes preference/grant/receipts persisted. Previewed undo, approved, saw four done receipts and original Sort marked undone. Independent byte check confirmed all five originals restored. Export displayed only preference JSON. Test permission revoked for owner handoff; saved Notes preference/history remain. Screenshot: ignored `data/mock-undo-preview.jpg`.
- **Final verification/handoff:** broader sample-generator reparse check also passes on Python versions before `Path.is_junction` existed; final full suite **48 passed, 1 warning in 7.83 seconds**. Staged whitespace check passed. No .env, SQLite database, generated samples, evidence image, node_modules or compiled UI is tracked. Browser-test server shut down cleanly; owner launches it with the documented command. Saving a sample-development checkpoint does not mark M1 or the full M2/personal-data gate complete.
- **Boundaries:** only generated sample root selectable; no personal folders, file-content upload, Windows setting/startup change, listening, background scheduling, message send or hosting. No new external documentation claim; model candidate/endpoint remain from prior official verification, not tested live.
- **Remaining:** **no live NVIDIA/Nebius inference, account credits or account-specific model availability verified; M1 is NOT complete**. These 48 checks are unit/local integration tests, not 48 live agent evaluations or the final five-user/30-scenario qualification. Full personal-folder safety gate stays closed; concurrent hostile local path replacement needs stronger handle-based hardening before widening scope. Starlette TestClient still emits its existing httpx deprecation warning.
- **Next exact task:** owner tries the sample UI. When credits arrive, put key only in ignored local .env, choose `VETO_MODE=nebius` or run `-Mode nebius`, ask two sample questions, record sanitized live evidence, and rerun blank-key check. Do not mark M1 complete from mock replies.

### 2026-10-05 — Milestone 0 and smallest Milestone 1 slice

- **Goal:** beginner-friendly local setup, generated sample files, backend, typed UI, verified NVIDIA/Nebius candidate; stop for owner trial.
- **Actual focused time:** approximately 15 minutes agent work, including setup and verification; not a measure of human work or total project effort.
- **Environment:** native Windows NT 10.0.26200, registry DisplayVersion 25H2/build 26200. Registry ProductName says Windows 10 Home Single Language (a legacy label); Windows 11 25H2 is inferred from build, not verified via Settings. Python 3.13.5, Node 24.12.0, npm 11.6.2, Git 2.50.0; VS Code executable found. No system-tool installation required. Dedicated Git repo initialized here on `codex/m0-local-shell`; no remote/publish. No milestone-passing commit yet, since owner/account gates remain open.
- **Changed files/behavior:** `.gitignore`, blank-key `.env.example`, MIT LICENSE, backend settings/provider/API and locked dependencies, React TypeScript UI and npm lockfile, Windows run script, sample generator, pytest suite, third-party notices, README and this log. Five generated fixtures stay in ignored `data/demo/Veto Demo Inbox`. No personal folder, setting, service, microphone, screen capture, or action tool access.
- **Commands actually run:** `git init --initial-branch=codex/m0-local-shell`; tool version checks; `python -m venv .venv`; pip install and freeze; `npm.cmd install --no-audit --no-fund`; `npm.cmd run build`; `.venv/Scripts/python.exe -m pytest -q`; `.venv/Scripts/python.exe -m pip check`; sample generator twice; `run-veto.ps1 -SetupOnly`; `run-veto.ps1`; `git check-ignore .env .env.local .venv frontend/node_modules data`; bundle search for credential identifiers; `git diff --check`; Windows listener inspection.
- **Observed passing evidence:** 15 backend tests passed (0.49 seconds in last successful run); Python dependency consistency passed; TypeScript and Vite build passed (28 modules); setup script completed; launch script started server; listener table confirmed only `127.0.0.1:8765`. Generator created five files then zero on repeat; tests prove byte preservation and rejection of a Windows junction. Git ignores local keys/dependencies/data. Built UI contained no `NEBIUS_API_KEY`, Authorization, or test-secret marker.
- **Browser smoke:** opened local UI, typed a sample Python-functions question, clicked Send; received explicit missing-key message, saw model badge and voice-off status. Screenshot saved locally at ignored `data/veto-preview.jpg`. No inference happened without a key; no fake fallback exists in app.
- **Handoff:** smoke-test server shut down cleanly with Ctrl+C; owner must run the launch script to reopen it. README opened in the Codex file panel. All source is currently uncommitted; no full milestone gate or passing commit is claimed.
- **Provider tests:** test-only mock HTTP transport covers model catalog/chat contract, missing model, bad key/access, rate/credit rejection, server error, timeout/no retry, and denied unofficial endpoint. These are unit checks, not live NVIDIA evaluations.
- **Failures resolved:** venv ensurepip, registry downloads, npm subprocesses and pytest temporary directories were blocked in sandbox; approved retries outside sandbox succeeded. First provider test searched for the word tools in a system message rather than the JSON field; corrected semantic assertion. Unknown API POST initially returned static-file 405; explicit API fallback now returns 404. Initial pytest temp parent missing; subsequent permitted test run passed.
- **Remaining warning:** Starlette 1.7.0 TestClient warns that its httpx integration is deprecated; 15 tests still pass. Runtime uses HTTPX directly, not TestClient. Review test transport when dependencies are upgraded; do not suppress warning silently.
- **Unverified / remaining problems:** no API key configured in project; no live `/models` or inference request, request ID, measured live latency or cost. Account registration, credit balance/expiry, account-specific model access, clean fresh checkout installation, three user-validated use cases and private interviews remain unverified. Full M0/M1 gates remain unchecked. Pricing/contest snapshot was not re-audited this session; no new contest or billing guarantee is made.
- **Sources checked Oct 5:** official Nebius quickstart and NVIDIA model page as linked in D06/D07; https://docs.tokenfactory.nebius.com/llms.txt and official https://github.com/nebius/token-factory-cookbook/blob/main/models/nemotron/nemotron3-nano-30b.md inspected as background. Selected ID comes from current official model page, not a guessed alias.
- **Next exact task:** owner follows README launch/key instructions and verifies two distinct live responses plus blank-key error. Record only sanitized request ID, model, latency, token counts and trial outcomes. Resume implementation only after owner reviews this first gate; do not begin M2 now.

### Proposed use cases — hypotheses, not interview findings

1. Student sorts generated class notes by file type after inspecting and approving a preview.
2. Student starts a reusable study-focus skill with a supported reversible setting.
3. Student drafts a short progress update from confirmed actions without sending it.

Validate these with real users privately. No interviews or credits are claimed as completed.

### YYYY-MM-DD — Milestone N

- **Goal:**
- **Actual focused time:**
- **Environment/commit:**
- **Changed files and behavior:**
- **Commands/checks actually run:**
- **Manual steps and observed result:**
- **Pass/fail and evidence:**
- **Verified external source URL/date (if used):**
- **Blocker and workaround:**
- **Next exact task:**

## Open questions

- Actual Nebius account credit, available NVIDIA model ID, regional endpoint, and function-call behavior.
- Wake-word and speech implementation that works acceptably on the user's machine, with measured false wakes/CPU and clear local/cloud audio boundaries.
- Reliable, affordable hosting for a sample-only judge demo; actual Windows build packaging.
- Whether email OAuth and screen help fit after core gates pass.
