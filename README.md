# UST Product Managers — Claude Session

Course materials for a hands-on training program teaching UST product managers how to work
effectively with Claude and Claude Code — from prompt fundamentals to context engineering,
agent design, and applying AI tooling to real product-management workflows (triage, cost
modeling, incident analysis, drift detection, and more).

This repository is organized as a series of dated class sessions. Each folder corresponds to
one session and contains that day's infographic, reference material, and hands-on demo code.

## Who this is for

Product managers with little or no coding background. Sessions assume no prior experience
writing software — later sessions include working demo applications that are meant to be run
and explored in a browser, not necessarily edited.

## Repository structure

```
UST-ProdManagers-Claude-Session/
├── 27JulyClass/       Session 1
├── 28July2026/        Session 2
├── 29July2026/        Session 2 (reference materials)
├── 29JulySession3/     Session 3
├── 03Aug2026/         Session 4 (intro)
├── 04Aug2026/         Session 4 (hands-on) — retail-ddd-ontology demo app
├── 05Aug2026/         Session 6 — context engineering demo app
```

Each session folder generally contains:

- **`UST_S*_Infographic.html`** — a self-contained, single-file visual summary of that
  session's concepts. Open directly in any web browser; no server required.
- **`files/` or `SessionFiles/`** — the session's supporting material: reference docs,
  sample datasets, and Python scripts used in exercises.
- Some sessions include a **demo application** (a small runnable project) used to make
  abstract concepts concrete. These have their own `README.md` inside their folder with
  setup instructions — start there before running any code.

## Getting started

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd UST-ProdManagers-Claude-Session
   ```
2. Open the infographic for your current session in a browser to review the day's concepts.
3. If the session includes a demo app (see folders under `04Aug2026/` and `05Aug2026/`),
   open that folder's own `README.md` for exact setup and run instructions — most require
   Python 3.10+ and, for the retail demo, Node.js 18+ as well.

## Session guide

| Session | Folder | Focus |
|---|---|---|
| 1 | `27JulyClass/` | Prompting fundamentals — worked through a prior-authorization triage and retail sales dataset |
| 2 | `28July2026/`, `29July2026/` | Agent specs, context design, and cost modeling for a retail stockout-alert agent |
| 3 | `29JulySession3/` | Applying Claude to operational data — CI incidents, duplicate payments, return abuse, escalations |
| 4 | `03Aug2026/`, `04Aug2026/` | Context engineering deep dive; hands-on `retail-ddd-ontology` app pairing Domain-Driven Design with an RDF/OWL ontology |
| 6 | `05Aug2026/` | Context health, drift detection, and dead-code analysis over a running codebase |

## Highlighted demo: `retail-ddd-ontology`

Located at `04Aug2026/retail-ddd-ontology/`, this is the most substantial hands-on project
in the repo: a small retail storefront (FastAPI backend, React frontend) built to teach
Domain-Driven Design alongside a parallel RDF/OWL ontology describing the same domain. It
includes its own:

- `README.md` — quick start and architecture overview
- `LEARN.md` — full instructor-led teaching guide (half-day workshop format)
- `DEMO.md` — a no-code walkthrough written specifically for product managers

If you only explore one thing in this repository, start there.

## Notes

- Infographic `.html` files are self-contained (no build step) — double-click or open with
  any browser.
- `.docx` and `.zip` files under `files/` folders are supplementary reference material from
  live sessions and are not required to complete exercises.
- Where a demo app's own `README.md` conflicts with anything above, defer to it — it is the
  source of truth for that specific project.
