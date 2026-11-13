# 03 — Decisions & Scope

A log of the decisions already made, why, and the defences prepared for the viva.
The point of writing these down: **named scope cuts must not silently creep back
in.** If a future idea reopens one of these, treat it as a real decision to revisit,
not a default.

## Decisions made

| # | Decision | Rationale |
|---|---|---|
| D1 | **DDPG-LSTM reinforcement learning — OUT** | No simulator/environment to train an RL agent against, and the data is cross-sectional (one row per runner), which is incompatible with the sequential state-transition setup RL needs. (Wu, 2025 is the DDPG-LSTM reference, kept as related work / future direction only.) |
| D2 | **VDOT — DROPPED** | It was an undisclosed dependency. Removed to keep the methodology self-contained and defensible. |
| D3 | **Component 1 = pipeline demonstration** | Dataset is synthetic and marathon-only; honest framing avoids over-claiming accuracy. |
| D4 | **Controller priority: PC > Fuzzy Feedback > Differential Evolution** | The Proportional Controller is the achievable core deliverable; fuzzy feedback is a stretch if time allows; DE is demoted to future work. |
| D5 | **Calendar placement: fixed + fallback for the FYP** | Adaptive placement is the long-term target but is out of scope for the timeline. A viva script is prepared (below). |
| D6 | **Adjustment polarity: easing (not make-up)** | Naji's own design choice, distinct from Connor et al. For beginner/recreational runners, easing after missed load is safer than piling missed load back on. |
| D7 | **Cross-distance conversion — [OPEN]** | Dash generalised approach vs. power-law baseline. Not yet locked. |
| D8 | **Recovery score: self-report primary, computed composite alternative** | Self-report is simplest for the user; composite is the fallback when objective markers are available. |

## Scope guardrails

- Keep ambition at **undergraduate level**. A clean, well-justified, working
  pipeline beats a half-built ambitious system.
- Anything cut above is **future work**, written up transparently — not hidden.

## Prepared viva defences

**"Why fixed calendar placement instead of adaptive?"**
Adaptive placement is the target design, but within the FYP timeline a fixed
placement with a fallback rule delivers a complete, testable plan generator. The
adaptive version is scoped as future work; the architecture leaves room for it.

**"Why not reinforcement learning, given the DDPG-LSTM literature?"**
RL needs an environment/simulator and sequential per-athlete trajectories. The
available data is cross-sectional, so there's nothing for an agent to interact
with. A rule-based + fuzzy + closed-loop-control design achieves adaptivity without
fabricating a simulator. (See D1.)

**"Your dataset is synthetic — how is the prediction valid?"**
The contribution is the **methodology and pipeline**, demonstrated end-to-end. The
synthetic, marathon-only nature is declared up front; accuracy figures are
illustrative of the method, not a claim about real-world runners. (See D3.)
