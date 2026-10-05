# Prompts to use with Codex

Open the folder containing these files in **Codex on your Windows laptop**. Do not paste your API key into chat. You should be able to copy these prompts exactly.

## First session: understand and start

> I am a beginner building **Veto**, a Windows assistant that answers to “Hey Veto,” for the Nebius x NVIDIA Global AI Hackathon Personal AI track. Read `AGENTS.md`, `README.md`, `PRODUCT_SPEC.md`, `SAFETY_POLICY.md`, `ARCHITECTURE.md`, `HACKATHON_RULES_AND_SOURCES.md`, and `IMPLEMENTATION_PLAN.md`. Inspect this Windows environment and the existing folder. Explain the project back to me in five simple sentences. Then implement **Milestone 0 and the smallest part of Milestone 1** in a new Git repository: scaffold a Python FastAPI backend and React TypeScript command UI, add a fixture-data generator, `.gitignore`, `.env.example`, and a simple Windows run script. Verify the latest official Nebius model catalog and choose an available NVIDIA Nemotron model; record URL, model ID, and date in `DECISIONS_AND_PROGRESS.md`. Make a real model call only once my Nebius key is set locally. Do not ask me to paste the key into chat. Run the app and relevant tests. Show me exact PowerShell commands and one browser action to verify the result. Keep the UI/API bound to loopback. Do not touch my personal folders or install startup/background services. The wake-word listener comes in Milestone 4 and must remain off by default until I enable it in Veto. Stop at the first acceptance gate and update progress.

## Resume at the next milestone

> Read `AGENTS.md`, `IMPLEMENTATION_PLAN.md`, `SAFETY_POLICY.md`, and `DECISIONS_AND_PROGRESS.md`, then inspect git status and the working app. Identify the next incomplete milestone. Implement only its smallest end-to-end slice, run the relevant checks, and show me how to verify it with sample data. Fix failures before claiming completion. Update progress with actual evidence and time spent. Preserve the last working commit. Explain any new concept simply and tell me my exact next action.

## If Codex proposes an unsafe PC action

> Pause runtime PC actions. Re-read `SAFETY_POLICY.md`. Show the specific proposed tool call, the allowed root or setting, approval step, undo behavior, and a fixture-data test. Implement the safety gate in backend code and test the denied case first. Do not run the action against my personal files until the fixture gate passes and I explicitly select a real folder in the app.

## If a dependency or API is unclear

> Verify this claim against current official documentation or the live account. Give me the source URL, what you observed, and what remains unknown. Record it in `DECISIONS_AND_PROGRESS.md`. Implement a small spike that tests the assumption. Do not fabricate a model ID, pricing, tool output, or completed test.

## End of each work session

> Run the milestone's appropriate tests and a quick manual smoke check. Update `DECISIONS_AND_PROGRESS.md` with what passed, what failed, exact commands, current git commit, estimated time spent, and the next one concrete task. Tell me in plain English what I can now do in the app. Make a commit if the gate passes. Do not start the next milestone automatically.

## When preparing the submission

> Read `HACKATHON_RULES_AND_SOURCES.md` and recheck the official Devpost rules today. Audit the public repository for license, setup, model/Nebius details, secrets, and personal data. Run the 30 cases in `EVALS_AND_DEMO.md`, test the judge link without login, and create an honest Devpost description and video script based only on demonstrated features. Flag every missing item in the submission checklist. Do not publish or submit for me until I approve the final public materials.

## Secret setup in plain English

An API key is like a password for the app to call Nebius. Codex should create `.env.example` with a blank `NEBIUS_API_KEY=` line. You copy it to an ignored `.env` file **on your laptop** and enter the key there. You do not send the key to Codex chat, GitHub, or the demo. If a screenshot shows it, redact it before sharing.
