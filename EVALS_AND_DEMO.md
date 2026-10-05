# Verification, judge demo, and submission evidence

## Meaningful evaluation set

Create **at least 30 reproducible scenarios** with generated fixture files and expected outcomes. Record each as `case ID, setup, command, expected behavior, observed behavior, pass/fail, latency, model ID, action IDs`. Use actual model calls for end-to-end agent cases. Unit tests can use a fake model adapter to isolate the policy engine. Do not count a static replay as a model evaluation.

| IDs | Scenarios | What success means |
| --- | --- | --- |
| F01–F05 | PDFs, screenshots, unknown files, duplicate names, mixed-case extensions | Correct preview and moves; unknowns left alone; no overwrite |
| S01–S06 | `..`, absolute path, symlink/reparse, revoked root, system folder, stale source | No path escape or write outside permission; clear reason |
| A01–A05 | Denied approval, altered plan hash, stop mid-run, retry, partial tool failure | No unapproved action or duplicate; truthful partial result |
| M01–M04 | Restart, preference edit, delete, export/import | Memory persists and changes actually affect next run |
| V01–V06 | Real “Hey Veto,” false wake, mic switched off, noisy transcription, mic unavailable, push-to-talk | Correct detection and transcript; no action on false wake; typing fallback works |
| W01–W03 | Focus setting supported, unsupported, rollback | Correct readback and truthful error; old state restorable where supported |
| P01–P04 | Malicious filename/file text, hidden instructions, oversized plan, unknown tool | No additional authority or executed code |

For each safety failure, add an automated regression check if it can reasonably recur. Run a clean end-to-end session after a release build. Do not use your actual Downloads folder as the test corpus.

Measure wake-word behavior separately with at least 20 intentional “Hey Veto” utterances and 20 ordinary/noise utterances. Record true detections, missed wakes, false wakes, average latency, and approximate CPU use on the target laptop. This small check is evidence for the demo, not a claim of production-grade accuracy. A false wake must still be blocked by the action approval gate.

## User trials

Ask at least five people to use the sample demo without a tutorial. Give each the same task: sort a sample folder by voice or typing, inspect the preview, approve, find the result, and undo. Capture time and whether they understand the approval screen. Ask what they thought the agent could access. Fix confusion before adding another feature. Record only anonymous feedback with consent.

## Demo video, maximum 2:50 target

| Time | Show |
| --- | --- |
| 0:00–0:20 | Messy sample folder and user problem |
| 0:20–0:45 | Visible mic opt-in, real “Hey Veto” command, transcript, and Veto's short spoken reply |
| 0:45–1:25 | Nemotron plan, exact file preview, approval, actual Explorer changes |
| 1:25–1:50 | Focus skill changes a real supported setting and opens a folder |
| 1:50–2:12 | Restart, remembered preference, rerun saved skill |
| 2:12–2:32 | Undo, permission roots, action record, drafted message |
| 2:32–2:50 | Name NVIDIA model and Nebius Token Factory; show honest results |

Do not imply the hosted sample filesystem is the owner's Windows filesystem. Record the Windows build for actual PC actions. A screenshot/tool trace can show where the real Nebius call occurs. Use original or licensed visual/audio material.

## Judge access

- Public repo with all necessary source, license visible at top, README with one-path setup, known limits, model configuration, `.env.example`, and no secrets.
- Demo URL or downloadable test build that runs without asking a judge to provide private data or pay. Give sample login only if necessary. Keep accessible through the official judging period.
- Hosted demo uses isolated sample data and a Reset button. Runtime Nemotron response still comes through Nebius. If a setting cannot be changed in browser hosting, label it a demonstration, while the Windows test build proves real actions.
- Public YouTube link under three minutes. Verify playback in private browser.
- Devpost text: problem, target user, what it does, how it works, exact NVIDIA model/Nebius path, original contribution, challenges, measured results, future work, and specific platform feedback.

## Submission QA checklist

- [ ] Devpost account joined; Personal AI track selected
- [ ] English project description matches built features
- [ ] Public repository, license, README, setup, sample data, no credentials
- [ ] Working demo URL or test build; accessible and free through judging
- [ ] Public YouTube video under three minutes, real functionality and required tech stated aloud
- [ ] Runtime NVIDIA model on Nebius demonstrated in code, logs, and video
- [ ] Privacy/permission controls and sample data clear
- [ ] Specific Nebius/NVIDIA feedback included
- [ ] All URLs tested while logged out; final entry submitted before Oct 30, 10:30 p.m. IST

## Honest claims

Use “drafts an email” until actual send is tested. Say “Hey Veto” works only after the real microphone/wake-word check passes on the target laptop. Use “selected folders” until broader access is explicitly implemented. Use “local memory with cloud model inference” when Nebius receives selected context. A working smaller agent is stronger than claiming a feature that fails for judges.
