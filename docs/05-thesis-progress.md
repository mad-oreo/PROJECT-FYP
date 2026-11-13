# 05 — Thesis Progress

## Chapter status

| Chapter | State | Notes |
|---|---|---|
| **Ch 1 — Introduction** | Drafted | Fix the **Lerebourg 2022 vs 2023** inconsistency here. |
| **Ch 2 — Literature Review** | Drafted | Structure 2.2 Domain / 2.3 Technique / 2.4 Related Works, 7–10 papers each; comparison-table format. |
| **Ch 3 — Research Methodology** | **ACTIVE** | Prose drafted in short, concise register (2–3 paragraphs per component). All three components designed. |
| **Ch 4 — Results / Evaluation** | Planned | Carries the K-gain justification and the ACWR-ceiling-as-heuristic framing. |

## Immediate next actions

1. **Lock the cross-distance conversion method** (Component 1): Dash generalised
   approach vs. power-law baseline. Document the chosen formula and its exact
   source. *(`docs/02-components-design.md`, [OPEN])*
2. **Finalise Chapter 3** — all three components fully written, in the concise
   paragraph register. K-value and ACWR-ceiling rationale stay deferred to Ch 4.
3. **Citation cleanup** — work through the flagged items in
   `docs/04-citations-and-sources.md`, especially verifying Gabbett (2016) before
   any direct citation of the 1.5 cap.

## Chapter 4 plan (when it starts)

- **K gain justification** — explain how the proportional gain was chosen and what
  behaviour it produces (responsiveness vs. stability of week-to-week adjustment).
- **ACWR ceiling as a heuristic** — frame the 1.5 cap honestly as a heuristic
  safety bound, citing **Bornn, Ward & Norman (2019)** that training schedule
  confounds the ACWR–injury relationship.

## Open questions (decide and record in `docs/03-decisions-and-scope.md`)

- [ ] Cross-distance conversion: Dash vs. power-law? *(D7)*
- [ ] Inference-time feature gap: reduced-feature model, imputation, or documented
      "demo uses full features" caveat? *(see C1)*
- [ ] Recovery score: confirm self-report primary vs. computed composite for the
      final implementation. *(D8)*
- [ ] Fuzzy Feedback Controller — attempt it (time-permitting enhancement) or hold
      as future work? *(D4)*

## Working reminders

- Thesis register = formal academic English, APA 7. Chat register = plain English.
- Methodology subsections stay short (2–3 paragraphs).
- Export diagrams as named PNGs for the `.docx` (e.g. *Figure 3.2 — Component 2
  pipeline flowchart*).
- Keep separating **sourced** material from **Naji's own design** in every section.
