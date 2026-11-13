# CLAUDE.md

> Read this file first. It is the entry point for the project. The `docs/` folder
> holds the detail. Everything here is the state we reached as of the handoff into
> Claude Code.

## What this project is

**Title:** *Adaptive Training Plan Recommendation and Race Time Prediction for
Distance Runners Using Machine Learning.*

**Author:** Ahmad Naji bin Abdul Rahman (ID 2025140485). Undergraduate Final Year
Project (FYP), intelligent systems / AI degree. **Not** a Master's or PhD — keep
scope and ambition at degree level.

**One-line pitch:** A system (possibly an app) that takes a runner's inputs (e.g.
easy pace, heart rate), predicts their race time for 5K / 10K / 21.1K / 42.2K,
builds a training plan to reach that goal, and then **adjusts the plan** as the
runner logs (or skips) their workouts. Consistent runners get pushed harder;
runners who miss sessions get an easier next week.

**Target users:** recreational and beginner runners.

### The three components

1. **Component 1 — Race time prediction.** Supervised ML regression trained on
   `train.csv`, then converted across distances from a marathon baseline.
2. **Component 2 — Training plan generation.** Rule-based engine with a fuzzy
   logic layer that sets training load, plus a session-synthesis stage that turns
   load into named workouts.
3. **Component 3 — Closed-loop plan adjustment.** A feedback controller that reads
   the runner's logged load each week and eases or progresses the next week, under
   a safety cap on load ramp.

Full detail: `docs/02-components-design.md`.

## Who you're working with (working style)

- **Chat tone:** plain, simple English. Get to the point. Direct.
- **Thesis tone:** formal academic English, APA 7, only when asked to write a
  section (literature review, methodology, etc.).
- **Methodology prose:** short and concise — two to three paragraphs per
  component, naming specific techniques and parameters directly. No padding.
- Naji **wants pushback.** Challenge weak assumptions and name scope/technical
  risk explicitly. He checks claims and finds errors independently — so don't
  bluff.
- He uses interactive HTML calculators / flowcharts to explore designs, and wants
  **PNG/figure exports** for diagrams to drop into Word.
- Primary thesis document is **Word (.docx)**, Times New Roman, justified, APA 7
  references with hanging indents.

## Non-negotiable rules

1. **Never cite without verification.** Every claim must trace to a specific
   passage/section/figure/table in a real source file. A fabricated paper
   ("Romaniszyn et al.") once slipped into a Chapter 2 draft and was caught — this
   is the **"Romaniszyn rule."** If a source can't be located in the corpus or a
   real database, it does not get cited. See `docs/04-citations-and-sources.md`.
2. **Separate sourced material from Naji's own design.** The membership functions,
   rule base, conflict-resolution ordering, rep structures, the **easing**
   adjustment polarity, and the **K** gain value are Naji's contributions — never
   present them as literature-derived.
3. **Flag secondary citations.** If a claim is only reachable through another
   paper, cite it as secondary (APA 7) and say so.
4. **Name scope cuts out loud.** Cuts already made (DDPG-LSTM RL, VDOT,
   adaptive calendar placement) must not silently creep back in. See
   `docs/03-decisions-and-scope.md`.
5. **Be honest about the data.** `train.csv` is **synthetic and marathon-only**.
   Component 1 is framed as a **methodological pipeline demonstration**, not a
   real-world accuracy claim. Say this plainly in the thesis.

## Where things are

```
fyp-repo/
├── CLAUDE.md                     <- you are here
└── docs/
    ├── 01-project-overview.md    <- problem, users, data flow
    ├── 02-components-design.md   <- the three components in detail
    ├── 03-decisions-and-scope.md <- decisions log + scope cuts + viva defences
    ├── 04-citations-and-sources.md <- citation rules + paper inventory + flags
    ├── 05-thesis-progress.md     <- chapter status + next actions + open questions
    └── 06-data-dictionary.md     <- train.csv columns, label, leakage flags
```

Suggested layout to add as the build starts (not yet created):
```
data/            raw + processed datasets (train.csv goes here)
src/             component_1_prediction/, component_2_plan/, component_3_control/
notebooks/       exploration + model training
figures/         PNG exports for the thesis
thesis/          chapter .docx files
references/       the ~26 source papers (.md / .pdf)
```

## Current status (start here)

- **Active chapter:** Chapter 3 (Research Methodology). Prose drafted in the short,
  concise register (2–3 paragraphs per component). All three components designed
  and documented.
- **Chapters 1 & 2:** drafted. Chapter 2 follows the lecturer's required structure
  — Domain (2.2), Technique (2.3), Related Works (2.4), 7–10 papers each.
- **Chapter 4 (results/evaluation):** planned, not started. Will carry the K-gain
  justification and the ACWR ceiling framing.

### Immediate next actions
1. **Lock the cross-distance conversion method** for Component 1 (Dash generalised
   approach vs. power-law baseline). Currently undecided.
2. **Finalise Chapter 3** with all three components fully written.
3. **Citation cleanup:** verify Gabbett (2016) for the ACWR 1.5 figure against the
   primary paper; confirm flagged secondary-source items before citing.

Full task list and open questions: `docs/05-thesis-progress.md`.

## Tools & environment

- **Dataset:** `train.csv` (Kaggle, synthetic, ~80,000 rows, 41 columns,
  marathon-only).
- **Citation/grep work:** the corpus is a set of `.md` / `.pdf` papers; use
  grep/awk to locate specific reference entries inside large compiled files.
- **Output:** thesis in `.docx`; figures as named PNGs (e.g. *Figure 3.2 —
  Component 2 pipeline flowchart*).
