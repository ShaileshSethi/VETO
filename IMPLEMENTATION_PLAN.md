# 25-day implementation plan

**Calendar:** Oct 4–28, 2026. Official deadline Oct 30, 10:30 p.m. IST. Target Oct 28. Each day is a planning slot, not an obligation to work while ill or busy. If starting later, compress polish and stretch work; protect the working core and submission time. The requested wake word and spoken replies increase the estimate to **55–80 focused hours**, including your manual testing. Track actual time in `DECISIONS_AND_PROGRESS.md`.

## Priority ladder

**P0 (must finish):** official registration; real Nemotron/Nebius runtime call; original Windows app; selected-folder file preview/move/undo; persistent memory; reusable skill with a bounded background check while the local process runs; safe judge access; public repo/license/README/video/feedback/submission.

**P1 (strong demo):** user-enabled local “Hey Veto” detector, push-to-talk fallback, original spoken replies; one reversible focus setting; clean UI; activity history; 30+ scenarios and five users.

**P2 (only after P0/P1 pass):** opt-in active-window help; schedule; email OAuth send; overlay; phone companion. A credible demo with P0 and P1 beats a broken feature list.

## Calendar and gates

| Days | Date | Focus and estimated effort | Must be true before moving on |
| --- | --- | --- | --- |
| 1–2 | Oct 4–5 | Join Devpost/Nebius, claim credits, set up GitHub/VS Code/Codex, interview five users; **3–5 h** | Repo boots, sample folder exists, three use cases documented |
| 3–5 | Oct 6–8 | Backend + UI shell + live Nemotron call; **6–9 h** | Typed prompt produces live Nebius response; model ID logged; key stays server-side |
| 6–9 | Oct 9–12 | Selected-folder permissions, file list, move preview/execute/undo, SQLite memory; **8–12 h** | Restart remembers preference; move/undo works; outside path and overwrite fail safely |
| 10–13 | Oct 13–16 | Agent tool planning, approval binding, one Windows focus action, resilient retries; **8–11 h** | Multi-step typed command works; duplicate retry does not repeat move; stop works |
| 14–17 | Oct 17–20 | Wake-word spike, push-to-talk, spoken reply, reusable skill, draft, error states; **12–16 h** | “Hey Veto” works after opt-in; mic off disables it; real voice and typed equivalent complete same workflow |
| 18–21 | Oct 21–24 | Package Windows test build, safe hosted demo, user trials and 30 evaluations; **9–13 h** | Judge can use sample data without credentials or access to owner's machine; metrics logged |
| 22–24 | Oct 25–27 | Polish, README, diagrams, feedback, sub-3-minute video, submission draft; **5–8 h** | Every public link works in logged-out browser; video shows live runtime call and real actions |
| 25 | Oct 28 | Submit and verify; **1–3 h** | Devpost entry shows final track, video, repo, demo/test build, description, feedback |
| Buffer | Oct 29–30 | Only submission fixes until official cutoff | No last-minute untested features |

## Milestone 0: account and repository

**Build:** new repo with docs from this pack, license choice, `.gitignore`, `.env.example`, minimal run scripts, sample generator. Keep key out of git. Decide Windows version and record it. Write five short interview notes privately.

**Manual check:** fresh clone/clean folder setup succeeds; sample folder contains expendable files only; credits are visible in Nebius account. **Evidence:** screenshots or redacted setup log, links, actual time spent. **Commit:** `docs: establish veto scope and setup`.

## Milestone 1: real AI brain

**Build:** Python API, React command bar, model adapter using exact available NVIDIA model ID and endpoint from current Nebius docs/account. One genuine call. Structured plan validation can start with a read-only tool. Key in backend environment only. Show provider/model badge and missing-key/network errors.

**Manual check:** ask two different questions, confirm different live responses and model ID in server logs; disable key and observe clear error; browser bundle contains no key. **Evidence:** sanitized request ID, model ID, latency, cost estimate. **Commit:** `feat: connect Nemotron through Nebius`.

## Milestone 2: files and memory

**Development exception, 5 October:** the owner explicitly authorized labelled mock chat and sample-only M2 implementation while awaiting credits. This permits the sample workflow to be tested before live M1 passes. It does not complete or replace the real NVIDIA/Nebius runtime gate. Personal-folder access remains unavailable.

**Build:** root selection, canonical path guard, bounded list, file move preview, exact approval, collision check, action journal, undo, SQLite preference CRUD/export, migrations. No file content access initially. Make sample folder generator and reset.

**Manual check:** sort mixed sample files, reopen app, see preference, undo, verify original bytes/locations; attempt `..`, absolute path, symlink/reparse, collision, and unapproved move. **Evidence:** case results and activity records. **Commit:** `feat: safe file sorting with undo and memory`.

## Milestone 3: multi-step skills and settings

**Build:** fixed tool schema, bounded planner, plan hash and per-action state, idempotency key, stop/retry, focus skill. Choose one Windows action whose old state can be read and restored; `open_allowed_folder` is a reliable second action. Record unsupported devices gracefully.

**Manual check:** typed “sort class downloads and get me ready to study” shows a plan, approvals and action receipts. Repeat after partial failure; no duplicate file move. Stop between steps. **Evidence:** state transitions and screenshot. **Commit:** `feat: approved multi-step focus workflow`.

## Milestone 4: “Hey Veto,” personality, and communication

**Build:** First test candidate wake-word detectors on the target laptop for recognition, false wakes, latency, and CPU use. Select an appropriately licensed local detector or train a small custom detector if practical; do not invent a capability. Add an explicit enable switch, visible mic indicator, one-click mute, and bounded post-wake recording. Add push-to-talk fallback with visible transcript and correction. Voice uses the same planner and permissions as typing. Add concise text-to-speech with an original voice and the distinct Veto personality; disclose whether speech is local or cloud. Saved skill definition/history persists. A bounded scheduled read-only check proposes changes even while the UI window is closed; record last run, next run, pause, and failure. Draft email/message text from selected facts, with separate recipient field; no silent send.

**Manual check:** after opt-in, say “Hey Veto” followed by a real request; see transcript, hear a short reply, and get the same action preview as typing. Turn mic off and verify no wake. Test a false wake and mic denial; no action occurs. Close UI while local process runs and observe a scheduled proposal on reopening. Restart preserves saved skill; draft changes nothing externally. **Evidence:** anonymized transcript, wake/false-wake measurements, scheduled run, and action IDs. **Commit:** `feat: wake word voice and reusable skills`.

## Milestone 5: evaluation and distribution

**Build:** Windows test build/installer or reliable run package; judge setup with sample data; hosted demo with virtual sample filesystem if feasible, live Nebius, reset; readable UI. If packaging or hosted demo stalls, prioritize an official-rule-compatible test build and a working demo link. Do not ship a hosted interface that can call your real PC.

**Manual check:** a fresh Windows setup succeeds using the README; judge test link works logged out; the 30+ scenario suite passes safety gates; five user trials recorded. **Evidence:** version/tag, result table, video clips. **Commit:** `chore: release judge build and evaluation`.

## Milestone 6: submission

**Build:** public repo, actual open-source license file, README with quick start and screenshots, architecture, safety, model and Nebius details, honest measured results, specific platform feedback, public YouTube video under three minutes, Devpost entry.

**Manual check:** open repo/demo/video in private browser; follow README from clean environment; check category Personal AI and actual final submission status. Store a copy of submitted text and links. **Commit/tag:** `v0.1-hackathon`.

## Time-saving rules

- Spend no more than **90 minutes** on a blocked integration before recording the blocker, switching to a simpler compliant route, and resuming P0.
- Start each session from `DECISIONS_AND_PROGRESS.md` and end by updating it. Keep a short “next exact task.”
- Use one vertical slice at a time. Do not ask Codex to write all milestones in a single turn.
- Use generated fixture files and a repeatable demo script from day 6 onward. Reuse these for manual checks and the video.
- Work on UI polish after the core action and undo path pass. Freeze new features on Oct 24.
- Save a working commit whenever a gate passes; avoid unreviewed mass refactors near the deadline.
