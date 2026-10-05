# Veto: Codex project pack

**Prepared 4 October 2026. Target: Nebius x NVIDIA Global AI Hackathon, Personal AI track.**

The planned Veto product is a Windows laptop assistant with selected-folder sorting, memory, focus skills, drafts, previews, and undo. **The current development build supports clearly labelled mock chat plus real, approved sample-file moves, undo, and local preference storage.** It starts in mock mode without API calls or credits. The real Nebius text adapter remains available, but **live NVIDIA/Nebius testing and the M1 acceptance gate are still pending**. Voice, settings, scheduled tasks, and personal-folder access are unavailable.

## Launch this build on Windows

Prerequisites: Python 3.11+, Node.js 22.12+ (or 24+), npm, Git, and a browser. Python 3.13.5, Node 24.12.0, npm 11.6.2, Git 2.50.0, and VS Code were found on the development laptop. No additional system tool was needed. A **virtual environment** keeps Python packages in this project, away from other projects.

Open PowerShell and run:

```powershell
cd 'F:\CODE BLUE\VETO AI\veto-codex-pack'
.\run-veto.ps1 -Mode mock
```

The script installs locked dependencies if needed, builds the interface, creates sample files without overwriting anything, and starts the local server. On a clean checkout, replace the first path with your checkout's folder. Internet is needed for first-time dependency installation. Open **http://127.0.0.1:8765** in your browser. Keep PowerShell open; **Ctrl+C** stops the server. No administrator account, startup service, microphone permission, or global execution-policy change is needed.

Type `How do I sort the sample files?` and click **Get sample reply**. Expect **MOCK · sample reply — no API call**. Mock replies are deterministic examples, not model inference; they do not execute actions. The sample files are under `data\demo\Veto Demo Inbox`; only sample text, JSON, an SVG image, and an unknown extension are used.

## Try sample sorting, approval, memory and undo

1. Click **Sample files & memory**. Choose **Veto Demo Inbox (generated samples)** and click **Allow selected sample folder**. No personal folder can be entered or selected.
2. Choose **Notes · study grouping**, then **Save preference**. **Export preference** displays JSON you can copy; **Reset preference** removes the saved choice and returns to the default.
3. Click **Preview sorting**. Review the exact source/destination table, total bytes, folders to create, skipped files and plan state. Nothing moves during preview. Unknown files stay where they are. For the supplied five files, expect four proposed moves.
4. Click **Approve exact moves**. Only the stored, validated plan can execute. Each receipt says `done` only after a Windows move succeeds. The fixed sorting rules run locally; neither mock replies nor live chat can execute them or see filenames.
5. Press Ctrl+C and relaunch Veto in mock mode. Refresh the browser and return to **Sample files & memory**. The folder grant, Notes preference and activity receipts should persist. The generator will not recreate originals that are already sorted.
6. In Activity, click **Preview undo** for the completed Sort, review the return paths, then **Approve exact undo**. All original sample bytes/locations should return. Empty sorting folders remain; no deletion tool exists.
7. Click **Revoke sample permission** to remove access. Revocation cancels waiting approvals and stops the remaining steps of an active batch. The completed part remains in the journal for undo after a fresh folder grant.

**Cancel plan** leaves files untouched; **Stop remaining moves** requests a stop between steps. A move already in flight may finish and will be journalled. If a file changes, a destination is occupied, a link/junction appears, or permission changes, execution is blocked rather than overwriting or silently adjusting the plan. Resolve the conflict manually in the sample folder and create a fresh preview. Do not use personal data to test conflicts.

SQLite stores preferences, the sample grant, exact plans and move receipts in ignored `data/veto.sqlite3`, schema version 1. The file service reads metadata only; file contents are not inspected or uploaded. Scope is bounded to a flat inbox and one level of known output folders, at most 50 moves and 10 MB per batch. No arbitrary root, recursive home scan, raw shell, delete or overwrite endpoint exists. Metadata identity and path checks run at preview, approval, and immediately before each move; Windows rename refuses an existing destination. Personal-folder access stays disabled; this sample development gate does not establish production resistance to malicious concurrent local filesystem changes.

## Add the API key locally

An API key is a password that lets Veto call Nebius. Create one in your [Nebius account](https://tokenfactory.nebius.com/) using the [official quickstart](https://docs.tokenfactory.nebius.com/quickstart). Confirm credits and model access in your account yourself; they have not been verified here.

When credits arrive, stop Veto with Ctrl+C. In the project folder, run:

```powershell
if (-not (Test-Path -LiteralPath '.env')) { Copy-Item -LiteralPath '.env.example' -Destination '.env' }
notepad .env
```

Inside Notepad, enter your key **after `NEBIUS_API_KEY=`**, set `VETO_MODE=nebius`, save, and close it. Keep the supplied endpoint/model initially. Do not put the key into a command, chat, screenshot, React source, or the question box. `.env` is ignored by Git and read only by the backend. `git check-ignore .env` should print `.env`. Environment variables take precedence over `.env`; remove an old `NEBIUS_API_KEY` from that session if it prevents the blank-key check. The optional script `-Mode` overrides the mode for that run only and restores the previous session value on exit.

```powershell
.\run-veto.ps1 -Mode nebius
```

Refresh the browser. Expect **NEBIUS MODE** and **Key configured · live testing pending**; this means the key exists, not that the account is authenticated. Ask `Explain Python functions in two simple sentences.`, then `Give me three sample study tips.` Successful responses show the actual provider/model, request ID if supplied, latency, and token usage. Logs show mode/model/latency without prompts or keys. Live errors never fall back to mock replies. For more offline development, relaunch with `-Mode mock`; even with a key present, mock mode makes no inference or catalog call.

The selected candidate is **`nvidia/Nemotron-3_5-Lightning`**, listed as a public endpoint by [Nebius's official NVIDIA model page](https://nebius.com/services/token-factory/models/nvidia-nemotron-models-inference), checked **5 October 2026**. The base URL is **`https://api.tokenfactory.nebius.com/v1/`**, from the official quickstart. Before each answer, the adapter checks `/models` for this exact ID using your key. If it is unavailable, select another NVIDIA model from your account's catalog and edit `NEBIUS_MODEL` locally. It never substitutes a model silently. Account availability, live inference, latency, and billing remain unverified until your trial succeeds. The first version caps each answer request at 1,024 output tokens, one active request, a 45-second HTTP timeout, and no automatic retries.

For the missing-key gate, temporarily clear only the key value in Notepad, restart, and submit a sample question. Expect the setup error. Restore the key locally afterward. Record sanitized request IDs/model/latency in the progress file, never your key or personal question text.

## Checks and troubleshooting

```powershell
.\run-veto.ps1 -SetupOnly
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m pip check
Push-Location frontend
npm.cmd run build
Pop-Location
```

Expected: setup complete, 48 tests pass, no broken Python requirements, and a successful TypeScript/production build. Unit transports and the explicitly labelled development mock are not live model evaluations. Tests cover byte-preserving move/undo, invalid approvals, path escapes, junctions, collisions, stale files, revocation, partial stop/failure, retry receipts, persistence, crash reconciliation, limits, and mock mode with HTTP client creation forbidden. Starlette TestClient emits one httpx deprecation warning; it does not affect these checks or runtime inference.

If PowerShell blocks a downloaded script, use `Unblock-File -LiteralPath .\run-veto.ps1` after reviewing it, then retry; this removes the downloaded-file marker on this project script only. If your computer enforces an organizational policy, follow that policy. If port 8765 is occupied by your previous Veto terminal, stop it with Ctrl+C. For broken/missing dependencies, rerun `-SetupOnly`. Invalid key/access, no credits, unavailable model, internet failure, timeout, and empty/provider errors are shown explicitly without displaying raw upstream bodies.

UI and API share **one loopback server**, with no CORS access for other websites. Origin, host, and per-process session checks protect requests. The browser receives no model credential. In mock mode nothing goes to Nebius. In Nebius mode, only submitted question text is sent; sample metadata stays local. No microphone, screenshot, personal-folder, Windows-setting, or startup/background service feature exists.

## Current acceptance gate

**Try this sample-only development gate.** On 5 October, the owner explicitly authorized mock mode and sample M2 work while credits are pending, overriding the original strict milestone sequence. Automated checks and the browser sort → process restart → approved undo trial passed. All five original sample files were verified byte-for-byte afterward. The test grant was revoked for handoff; the saved Notes preference and receipts remain as demonstration evidence. Full M0 account/user research checks remain pending; **M1 remains incomplete and live NVIDIA testing is pending**. M2 personal access and wider features are not enabled. See [DECISIONS_AND_PROGRESS.md](DECISIONS_AND_PROGRESS.md).

The source has an MIT license; see [LICENSE](LICENSE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). The owner-authorized source repository is [ShaileshSethi/VETO on GitHub](https://github.com/ShaileshSethi/VETO), with commits pushed to `main`. API keys, local SQLite state, generated sample files, screenshots, dependencies and compiled UI are ignored and excluded from the source repository.

## Which file answers which question?

| File | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Instructions Codex reads while working in the repo |
| [PRODUCT_SPEC.md](PRODUCT_SPEC.md) | User experience, features, scope, and demo story |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Components, data flow, tool contracts, persistence |
| [SAFETY_POLICY.md](SAFETY_POLICY.md) | PC access, approvals, path checks, undo, stop behavior |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | 25-day schedule, milestones, acceptance gates |
| [EVALS_AND_DEMO.md](EVALS_AND_DEMO.md) | Real tests, judge demo, deployment/test-build checks |
| [HACKATHON_RULES_AND_SOURCES.md](HACKATHON_RULES_AND_SOURCES.md) | Verified rules, dates, credits, citations, and open questions |
| [CODEX_PROMPTS.md](CODEX_PROMPTS.md) | Ready-to-paste prompts for starting and resuming work |
| [DECISIONS_AND_PROGRESS.md](DECISIONS_AND_PROGRESS.md) | Actual choices, progress, blockers, evidence |

## Rules of the project

The app must make a **real runtime call** to an NVIDIA open model on Nebius Token Factory or run on Nebius AI Cloud. Codex can write code with any model; that does not replace the runtime requirement. The submitted repository must be original, public, and open source. This pack is planning material, not evidence that the app has been built.

Use [Blinky](https://github.com/KingSahil/Blinky) as a design reference for a command bar, voice, and opt-in screen guidance. Make Veto's actions, permissions, memory, and undo visibly yours. Do not copy Blinky code/assets without verifying its license and complying with it.

## Time and expectation

There are **25 calendar days from Oct 4 through Oct 28**, including an intended two-day submission buffer before the official Oct 30 deadline. With the wake word and spoken replies included, expect roughly **55–80 focused hours** across setup, coding with Codex, hands-on testing, deployment, and video. This is an estimate, not a promise. If you start late, use the priority order in the implementation plan; a reliable file-action, memory, and voice demo matters more than extra integrations.

The app must never be tested first on your personal documents. Start with generated sample files in a dedicated test folder. The real user grants specific folders later.
