# 01 — Project Overview

## Problem

Recreational and beginner runners often train without a structured, personalised
plan. They set a race goal, but have no reliable way to (a) know whether the goal
is realistic, (b) get a plan calibrated to their current fitness, or (c) keep the
plan honest when life interrupts training. Generic plans are static — they don't
respond to whether the runner actually completed the sessions.

## What the system does

A three-stage pipeline:

```
 user inputs (fitness markers)
        │
        ▼
 [ Component 1 ]  ML race-time prediction  → predicted time for 5K / 10K / 21.1K / 42.2K
        │
        ▼
 [ Component 2 ]  training-plan generation → a periodised plan (duration set by distance)
        │
        ▼
 user trains and logs completed / skipped sessions
        │
        ▼
 [ Component 3 ]  closed-loop adjustment   → next week eased or progressed
        │
        └────────── loop back into the plan each week ──────────┘
```

- **Inputs (user-facing):** fitness markers such as easy pace and heart rate. Note
  the model in Component 1 was trained on a wider feature set than a runner can
  realistically type in — see the *inference-time feature gap* open issue in
  `docs/02-components-design.md`.
- **Plan duration:** determined by the target distance (longer races → longer
  plans).
- **Adjustment trigger:** the runner uploads workout results. Consistency →
  tougher next block; missed sessions → easier next block.

## Target users

Recreational and beginner distance runners. This shapes everything: the plan
templates lean on sub-elite / recreational benchmarks (Knopp et al., 2024), the
safety constraints are conservative, and the language to the user is simple.

## Scope framing (important)

This is an undergraduate FYP, so the bar is a **working, well-justified
methodological pipeline**, not state-of-the-art accuracy. In particular:

- The dataset is **synthetic and marathon-only**, so Component 1 is presented as a
  **pipeline demonstration** — the method is sound and reproducible; the headline
  error numbers are not a claim about real runners.
- Several ambitious extensions were deliberately scoped out (reinforcement
  learning, adaptive calendar placement, differential-evolution control) and are
  documented as future work rather than silently dropped. See
  `docs/03-decisions-and-scope.md`.

## How the components connect (data contract)

| From → To | What passes between them |
|---|---|
| C1 → C2 | predicted finish time for the chosen distance (the goal the plan is built around) |
| C2 → user | a structured plan: weekly volume, phase, and named sessions with target intensity zones |
| user → C3 | logged sessions, each with a load value (session-RPE) |
| C3 → C2/plan | a scaling signal for next week's prescribed load (ease or progress), bounded by the safety cap |

Keeping these interfaces clean is what lets the three components be built and
tested independently.
