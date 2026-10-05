# Product specification: Veto

## One sentence

Veto is a Windows assistant you can call with **“Hey Veto”** or type to. It speaks back, completes selected laptop tasks, and lets the owner see, approve, and undo its work.

## Users and problem

The first user is a student whose Downloads and project folders get messy, who repeatedly changes a few laptop settings to study, and who drafts routine updates. A natural-language command should join these steps. The target benefit is fewer manual steps, less time spent finding files, and confidence that the assistant will not damage other folders.

Interview five target users before polishing. Record their actual repetitive tasks, the action they trust least, and what a successful result would look like. Do not put their private information into the public repo.

## Main experience

1. The owner explicitly enables the local wake-word listener. “Hey Veto” wakes it, followed by one spoken request. A small desktop command window always supports typing and push-to-talk as alternatives. The transcription is visible and editable before an action.
2. They ask: “Organize my class downloads, then set up focus mode.”
3. Veto uses Nemotron to choose from registered capabilities and explain a short plan. Its proposed actions include exact source and destination files, allowed folder, and intended setting change.
4. The owner approves the proposed file batch. The app validates paths again and moves files. It shows each success/failure and an **Undo** button. A separate focus-mode action opens the study folder and applies only a supported reversible setting.
5. Veto remembers the chosen sorting preference. After restart it can apply that preference to a new sample file, with a new preview and approval.
6. Veto answers in a concise spoken voice and shows the same answer as text. The owner can ask it to draft a message. Veto displays the intended recipient (if selected), subject, and full body. It does not send merely because it drafted. Actual sending is a later gated capability.

## Personality and voice

Veto is composed, observant, and a little witty. It speaks like a helpful technical companion: short sentences, clear status, one light remark when appropriate, no constant jokes. It admits uncertainty and never claims an action succeeded before the tool confirms it. It uses the owner's name only if the owner sets that preference. Example original lines: “I found eight files. Three look like lecture notes. Shall I sort them?” and “Done. Everything is in place, and I kept an undo path.” The personality prompt affects tone only; it cannot override the permission policy. Use a clearly distinct voice and visual identity rather than copying a film character's voice or lines.

## Hackathon must-have features

| Feature | Acceptance check |
| --- | --- |
| Real NVIDIA model via Nebius | One live request and logged model ID; no canned response in qualification path |
| Keyboard, wake word, and speech | “Hey Veto” is detected locally after opt-in; a real microphone request is transcribed and answered aloud; typing and push-to-talk remain available |
| Local file control | Selected sample folder can be listed, previewed, grouped, moved, and fully undone |
| Persistent memory | A sorting preference remains after process restart, can be edited/deleted/exported |
| Reusable skill | “Tidy class downloads” or “focus mode” runs again and shows its definition/history |
| Continued operation | A bounded scheduled check runs while the UI window is closed but the local process remains active, then presents a proposal on reopening |
| System action | At least one supported Windows action, such as opening a study folder or reversible brightness/volume setting, is demonstrably executed |
| Safety | Denied outside-folder path, symlink escape, collision, and unapproved action cases pass |
| Judge access | Windows test build plus safe hosted demo or equivalent official-rule-compliant test access |

## Stretch features in priority order

1. **Opt-in screen help:** screenshot active window only after the user clicks Look at my screen; interpret it using accessibility/OCR and explain where to act. Add an overlay highlight only when grounded to a real element. Do not make visual clicking a required demo step.
2. **Startup convenience:** optional user-enabled Windows startup entry and tray control so the bounded scheduled check can run after login. Never move files in background without an explicitly granted policy; default to proposing changes.
3. **Actual email send:** one OAuth integration, verified recipient, displayed full draft, and an explicit Send click. A sent-message receipt proves the call occurred once. Never claim sending works if only a draft exists.
4. **App control and Android companion:** post-hackathon unless all gates above pass early.

## The signature demo

The screen shows a sample `Veto Demo Inbox` folder with mixed lecture PDFs, screenshots, and other documents. The user enables the listener and says “Hey Veto, organize my class downloads and set up focus mode.” A visible transcript appears and Veto speaks a short acknowledgement. It previews exactly where each item will go. After approval, Windows Explorer shows real file moves; the focus skill changes a setting and opens a folder. The app explains that a remembered preference guided the grouping. The user restarts Veto, adds a new file, reruns the skill, and undoes the file batch. A draft message summarizes the operation. The active model and Nebius runtime are named in the video.

## Interface requirements

- A command bar or compact window with typed input, push-to-talk, user-enabled wake-word toggle, microphone indicator, spoken-response toggle, status, and stop button.
- A plan card for each proposed action. Distinguish proposed, approved, running, done, failed, and undone.
- File preview table with exact source and destination; collision warnings; count and size.
- Permissions screen listing allowed roots, what each tool can do, revoke button.
- Memory page with source, last updated, edit/delete/export.
- Skills page with definition, run, pause, and last result.
- Activity page with action ID, timestamp, result, and retry/undo where applicable.
- Clear provider badge for local speech versus a network provider; never imply all data remains on-device when Nemotron receives selected text.

## Scope boundaries

Veto may see only user-selected folders and explicitly granted screen captures. No generalized shell tool. No deletion in the hackathon build. No arbitrary browser login or session scraping. No silent email or message send. Do not present a scripted animation as a working agent.

## Product success measures

- Task completion rate across a fixed evaluation set of at least 30 scenarios (see `EVALS_AND_DEMO.md`).
- Zero unapproved writes in the evaluation set; zero path escapes; zero duplicate sends/moves after retries.
- Time from command to approved completion and estimated time saved compared with manual workflow, measured on the same task.
- At least five users can understand the preview and undo without instruction. Record feedback and failures honestly.
