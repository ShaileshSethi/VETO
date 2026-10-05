# Hackathon facts and source register

**Checked:** 4 October 2026. Before submitting, check the official pages again and record differences.

| Fact | What it means for Veto | Source |
| --- | --- | --- |
| Deadline: **Oct 30, 2026, 10:00 a.m. PDT = 10:30 p.m. IST** | Target completed submission Oct 28; keep Oct 29–30 as buffer | [Schedule](https://nebiusglobalaihackathon.devpost.com/details/dates), [rules §1](https://nebiusglobalaihackathon.devpost.com/rules) |
| Build a working app with at least one **NVIDIA open model** on **Nebius Token Factory or AI Cloud** | Implement a live Nemotron call, not a mocked or development-only call | [Overview](https://nebiusglobalaihackathon.devpost.com/), [rules §4](https://nebiusglobalaihackathon.devpost.com/rules) |
| Token Factory route means a **runtime inference API call** | Keep runtime logs and code showing the call | [Rules §4](https://nebiusglobalaihackathon.devpost.com/rules) |
| Personal AI: always-on, private, memory, reusable skills, chosen tools, daily actions | Demonstrate persistent memory, a repeatable skill, PC actions, and permissions | [Overview](https://nebiusglobalaihackathon.devpost.com/) |
| Suggested tools include NemoClaw, OpenShell, Hermes Agent, Nebius Serverless | Optional inspiration; do not make every one a dependency | [Overview](https://nebiusglobalaihackathon.devpost.com/) |
| Stage 1 viability; stage 2 equal scores for implementation, design, impact, idea | Prove each with functioning app, coherent UI, user evidence, and original workflow | [Rules §6](https://nebiusglobalaihackathon.devpost.com/rules), [judging update](https://nebiusglobalaihackathon.devpost.com/updates/46204-here-s-how-judging-works) |
| Public repo, open-source license, README; working demo URL or test build; English description; public YouTube video **under 3 minutes**; platform feedback | Submission checklist is mandatory | [Rules §4](https://nebiusglobalaihackathon.devpost.com/rules) |
| Judges may judge without testing; testing access remains free and unrestricted through judging | Video must show real actions; maintain a safe judge demo | [Rules §4](https://nebiusglobalaihackathon.devpost.com/rules) |
| Significant updates must be explained if using a pre-existing project | New repository preferred; cite libraries | [Rules §4](https://nebiusglobalaihackathon.devpost.com/rules) |
| Individual entrants must meet local age-of-majority rule | Confirm eligibility when joining | [Rules §3](https://nebiusglobalaihackathon.devpost.com/rules) |

**Prize note:** Personal AI track winner receives an NVIDIA Jetson Orin Nano. Overall awards are $20,000, $10,000, and $6,000. A project can receive one overall **or** track prize plus one bonus prize, per the rules. No result is guaranteed. [Prizes and rules](https://nebiusglobalaihackathon.devpost.com/rules).

**Credits:** [Hackathon resources](https://nebiusglobalaihackathon.devpost.com/resources) lists $25 Token Factory credit with code `NEBIUS-DEVPOST-GLOBAL26`, plus another $25 through the [Nebius Builder Program](https://dev.nebius.com/builders), subject to account eligibility and actual redemption. Confirm balance and expiration in the account. A ChatGPT subscription does not pay Nebius API charges. [Token Factory quickstart](https://docs.tokenfactory.nebius.com/quickstart) explains API-key setup and OpenAI-compatible requests. Pick the current model ID in the logged-in catalog; do not hard-code an ID from this planning document without verification.

**Submission package:** track selection; project description; public source link with license and setup; working demo URL or test build; public YouTube demo; specific feedback on Nebius/NVIDIA; note on substantial updates if applicable. The README must say what components run locally, what data goes to the model provider, and how judges use sample data. Keep test credentials separate and safe. [Official rules](https://nebiusglobalaihackathon.devpost.com/rules).

**Known ambiguity:** the resources page suggests city awards may be open to submissions associated with a participating city without attendance; the formal rules frame them around attendance. This does not affect the Personal AI entry. Prefer the formal rules or ask the organizer if pursuing a city award.

## Questions to verify during build

- Which NVIDIA Nemotron model is available to this account today, and does its chosen API support the required tool-call format? Record ID, endpoint, and one successful response.
- Are credits active and what are the account limits? Do not assume every account receives both offers.
- What hosting or test-build form gives judges a usable demo while keeping local PC operations isolated? Test without personal credentials.
- Does a live email integration fit the time and provider terms? Label drafting and sending separately.

## Reference product

[Blinky](https://github.com/KingSahil/Blinky) is a design reference for a desktop command bar, screen guidance, voice, and bounded actions. Its [README](https://github.com/KingSahil/Blinky/blob/main/README.md) and [security notes](https://github.com/KingSahil/Blinky/blob/main/local-docs/SECURITY-AND-RISKS.md) describe the product and remaining security work. The GitHub repository metadata showed no detected license on Oct 4 despite an MIT badge in the README. Verify permissions before borrowing any code or assets. Veto should have its own source and identity.
