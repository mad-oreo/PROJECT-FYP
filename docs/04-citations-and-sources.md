# 04 — Citations & Sources

Citation integrity is the **#1 value** on this project. This doc holds the rules,
the paper inventory with verification status, and the specific items that still
need fixing.

## The rules

1. **Romaniszyn rule — never cite without verification.** Every claim must trace to
   a specific passage / section / figure / table in a real source. A fabricated
   "Romaniszyn et al." paper once entered a Chapter 2 draft and was caught. If a
   source can't be located in the corpus or a real database, it is not cited.
2. **In-paper location markers.** When attributing a claim, note *where* in the
   source it comes from (section / table / figure), so it can be re-checked.
3. **Secondary citations get flagged (APA 7).** If a claim is only reachable
   through another paper, use the "as cited in" form and say so explicitly.
4. **Sourced vs. original.** Don't dress up Naji's own design (capacity bands, the
   C1–C4 rule base and its priority ordering, rep structures, the A-n items in
   `ASSUMPTIONS.md`, easing polarity, K gain) as literature-derived.
5. **APA 7 formatting.** In-text citations alphabetised and separated with
   semicolons; references with hanging indents. Cite by **author, year** — a
   framework/product name is not a citation (e.g. "DeepRace framework (2024)" is
   **not** valid).

## Paper inventory (verification status)

Status legend: **[READ]** = content read directly and confirmed; **[CH2]** = cited
in the existing Chapter 2 draft; **[VERIFY]** = author/year not yet confirmed
against the file — check before citing; **[FLAG]** = has an open issue (see below).

| Source file | Likely citation | Role in project | Status |
|---|---|---|---|
| `Quantitative_Analysis_of_92_12_Week.md` | Knopp et al. (2024), *Sports Medicine – Open* | Five-zone intensity model; volume/intensity benchmarks for recreational plans | **[READ]** [FLAG] |
| `A_reinforcement_learning_-_enabled_system_for_personalised.md` | Zhou & Zhou (2025) | Source for ACWR 1.5 cap; RL-enabled personalised training (context) | **[READ]** |
| `Adaptive_Athlete_Training_Plan_Generation.md` | Connor et al. (2022) *(verify)* | Closed-loop controller **architecture** for Component 3 | **[VERIFY]** |
| `DDPG-LSTM_Framework_for_Personalized_Athlete_Training_Plan.md` | Wu, J. (2025), *Informatica* 49 | DDPG-LSTM — **scoped out**; future work / related work | **[READ]** |
| `gradient_boost_paper1.md`, `Using_ML_to_support_marathon_runners.md` | Smyth et al. (2022) | Six ML algos, Gradient Boosting best; ACWR disruption risk + CBR plan rec | **[READ]** [CH2] |
| `Running_Pace_Adjustment_..._Fuzzy_Logic_and_Machine_Learning.md` | Dziomdziora & Taibi (2022) *(verify)* | Precedent for **fuzzy logic** in training (technique only) | **[VERIFY]** |
| `Win_Your_Race_Goal_..._Prediction_of.md` | Dash (2024) *(verify)* | Cross-distance conversion candidate (generalised approach) | **[VERIFY]** |
| `Analysis_of_Training_Optimization_..._Genetic_Algorithm.md` | Feng et al. (2024) — AH-GA | Related work (GA-based training optimisation) | **[CH2]** [FLAG] |
| `A_fitness_training_optimization_..._heart_rate_prediction_under.md` | Zhu et al. (2022), *Methods* | HR-zone prediction via LSTM (related work) | **[READ]** [CH2] |
| `Scientific_Programming_-_2022_-_Zhou_-_Sports_Achievement_Prediction...` | Zhou (2022) | DNN beats regression/grey models for sports prediction (related work) | **[CH2]** |
| `DeepRace_GRU-Based_Sequence_Modeling_Framework_for.md` | Zhou (2025) *(verify)* | GRU race-time modelling (related work) | **[VERIFY]** [FLAG] |
| `Prediction_of_Marathon_Performance_using_Artificial_Intelligence.md` | *(verify)* | Marathon performance prediction (related work) | **[VERIFY]** |
| `A_simple_relationship_for_predicting_marathon.md` | *(verify)* | Simple marathon-time relationship (prediction baseline candidate) | **[VERIFY]** |
| `results_from_the_NURMI_Study__Step_2_.md` | Braschler et al. (2025) *(verify)* | NURMI endurance study (context) | **[VERIFY]** |
| `Improving_Recommender_Systems_using_Hybrid_Techniques_of.md` | Vairavasundaram et al. (2022) *(verify)* | Recommender-systems technique (domain) | **[VERIFY]** |
| `Estimating_the_cost_of_training_disruptions_on_marathon_performance.md` | Feely et al. (2023) | Training-disruption cost (motivates adjustment); Component 2 P2/P4/T1 | **[READ]** (verified 11–13 Nov 2026) |
| `Physiology_and_Pathophysiology.md` | *(verify)* | Physiological grounding | **[VERIFY]** |
| `Systematic_review_..._decision_fatigue...md` | *(verify)* | Decision-fatigue review (motivation for automation) | **[VERIFY]** |
| *(verification log)* | Daniels (2022), *Daniels' running formula* (4th ed.) | Component 2: phases (Fig. 10.2), volume, long run, M/T/I/R caps, long-track sessions (Table 16.2) | **[READ]** (verified 11–13 Nov 2026; **page numbers TBC**) |
| *(verification log)* | Campos et al. (2022) | Component 2: P6 ≥ 70% easy; low intensity = RPE 1–4 | **[READ]** (verified 11–13 Nov 2026) |
| *(verification log)* | Foster et al. (2001) | Component 2: session-RPE load (S6) | **[READ]** (verified 11–13 Nov 2026) |
| *(verification log)* | Goldberg et al. (2025) | Component 2: recovery questions (sleep) | **[READ]** (verified 11–13 Nov 2026) |
| *(verification log)* | Plateau et al. (2022) | Component 2: P2b 5K plan length | **[READ]** (verified 11–13 Nov 2026) |
| *(verification log)* | Relph et al. (2023) | Component 2: P2b 5K plan length | **[READ]** (verified 11–13 Nov 2026) |
| Others in corpus (AI track & field, anomaly detection, big-data training, IMU fatigue, 50-mile, dynamic activity recommendation, survey of recommender systems) | *(verify)* | Domain / technique / related work | **[VERIFY]** |

> Gabbett (2016), Bornn et al. (2019), Turnwald et al. (2025), Lerebourg, Huang &
> Wang (2026), and Romaniszyn (2021) are discussed under **Flagged items** below —
> several are referenced *through* other papers rather than held as standalone
> files.

## Flagged items (fix before final submission)

1. **Gabbett (2016) — ACWR 1.5 figure.** Real paper (*The training–injury
   prevention paradox*, Br. J. Sports Med., 50(5), 273–280) but in this corpus it
   appears **only inside other papers' reference lists**, not as a readable source.
   **Do not cite Gabbett directly for the 1.5 cap until the primary paper is read.**
   Until then, attribute the operational 1.5 cap to **Zhou & Zhou (2025)**.
2. **Knopp et al. (2024) — zone-model origin.** Knopp **adapted** the five-zone
   model from **Jamnick et al.** and **Seiler** (confirmed in the paper's Table 2
   and methods). Do **not** credit Knopp as the originator of the zone framework.
3. **Lerebourg — year inconsistency.** Cited as **2022 in Chapter 1** but the
   official year is **2023**. Pick one and make it consistent across all chapters.
4. **Feng et al. (2024) — author count.** Has **three** authors (Feng, Wen, and
   Fu), not two. Fix any two-author in-text form.
5. **"DeepRace framework (2024)" — invalid citation form.** Cite by author/year
   (**Zhou, 2025** per prior notes) — confirm against the `DeepRace_GRU...` file.
6. **Romaniszyn (2021) — secondary only.** Accessible only through Wu (2025). If
   used, cite as secondary ("as cited in Wu, 2025") — and double-check it is a real
   reference, given the earlier fabricated-paper incident.
7. **Huang & Wang (2026).** Previously marked **verified** as a fuzzy-logic
   precedent — confirm the source file/entry exists in the corpus before final
   citation.

## Chapter 2 structure (lecturer's required shape)

- **2.2 Domain** — 7–10 papers
- **2.3 Technique** — 7–10 papers
- **2.4 Related Works** — 7–10 papers

Chapter 2 already uses a comparison-table format (Author/Year · Title · Technique ·
Relevance · Limitation) — keep that consistent.

## Component 2 source map (verified 11–13 Nov 2026)

The canonical map from Component 2 rules to sources, from Naji's verification log
("Log #" = row in that log). `components/component2/config.py` is tagged from this table;
own-design rows are listed with code locations in `ASSUMPTIONS.md`. Daniels page
numbers are not verified yet: cite chapter/section and mark **page TBC**.

| Rule / value | Source tag | Log # |
|---|---|---|
| Z: % max HR, RPE ranges, zone names | Knopp et al. (2024), Table 2, p. 5 | 5 |
| Z: pace targets, RPE midpoints 1.5–9.5 | OWN DESIGN | – |
| Z: zone ↔ Daniels E/M/T heart-rate bands | Daniels (2022), Ch. 4 | 23 |
| C: bands, rules C1–C4, priority | OWN DESIGN | – |
| C: runs/week 3/4/5 | Daniels (2022), Ch. 16 "Novice Training"; Knopp et al. (2024), Table 3 (4.1 ± 0.9) | 24, 9 |
| C: hard sessions 1/2/2 | Daniels (2022), Ch. 16; Knopp et al. (2024), Discussion p. 10 (citing Midgley 2007, Boullosa 2020: secondary) | 24, 12 |
| Recovery questions, 1–5 scale, weekly totals | Daniels (2022), Ch. 2, Table 2.1 "Stress Table"; Goldberg et al. (2025), Abstract; Smyth et al. (2022), §2.1.3 p. 793 | 35, 37, 36 |
| Recovery cut-offs 3–7 / 8–11 / 12–15 | OWN DESIGN | – |
| V1, V3, V4, entry minimums | OWN DESIGN | – |
| V2: hold 3–4 weeks, +1.6 km per weekly run | Daniels (2022), Ch. 4 "Training Suggestions"; Ch. 13 "Phase I" | 21 |
| Peak targets: marathon Standard 58, Progressive 75 | Knopp et al. (2024), Results pp. 7–8 (58.6 ± 6.4; 75.5 ± 8.5 km) | 8 |
| Peak targets: all other cells | OWN DESIGN | – |
| L1: 30% < 64 km; min(25%, 150 min) ≥ 64 km | Daniels (2022), Ch. 4 "Long Runs and Increasing Mileage" | 19 |
| L2: marathon 32 km | Knopp et al. (2024), Results p. 8; Conclusions point 4 | 10 |
| L2: 150 min | Daniels (2022), Ch. 4 "Training Suggestions" | 20 |
| L2: 5K 12, 10K 16, HM 20 km | OWN DESIGN | – |
| L3: long run in Z2 | Knopp et al. (2024), Table 2; Daniels (2022), Ch. 4 | 5 |
| T1: marathon 3 weeks | Knopp et al. (2024), Conclusions point 5; Feely et al. (2023), Introduction | 16 |
| T1: HM 2 weeks | Bosquet et al. (2007), as cited in Knopp et al. (2024), Discussion p. 11 | 13 |
| T1: 5K/10K 1 week | OWN DESIGN | – |
| T2: 25% per week | OWN DESIGN, inside Knopp et al. (2024), Results p. 9 (22–31%) | 11 |
| T2: race week 50% | Knopp et al. (2024), Results p. 9 (final week 46–54%) | 11 |
| T3: keep intensity and frequency | Bosquet et al. (2007), as cited in Knopp et al. (2024), Discussion p. 11 | 13 |
| P1: 24-week cap | Daniels (2022), Ch. 10 "Adapt the Phase Lengths as Necessary" | 17 |
| P2: minimums 6/9/12 | OWN rule built on Daniels (2022), Fig. 10.2 | 17 |
| P2: marathon 12 weeks | Feely et al. (2023), Abstract; Smyth et al. (2022), p. 794; Knopp et al. (2024), p. 6 | 34 |
| P2: Conservative marathon 18 | Daniels (2022), Ch. 16, Table 16.2 | 31 |
| P2b: 5K about 9 weeks (8–12) | Plateau et al. (2022), pp. 1–2; Relph et al. (2023), Methods | 32, 33 |
| P3: phase allocation | Daniels (2022), Ch. 10, Fig. 10.2 | 17 |
| P4: no hard sessions in week 4 | Daniels (2022), Ch. 16 (4-week cycle plans); Feely et al. (2023), Introduction | 26, 16 |
| P4: 80% volume | OWN DESIGN | – |
| P5: easy share by phase | OWN DESIGN | – |
| P6: ≥ 70% easy | Campos et al. (2022), Abstract p. 305; low intensity = RPE 1–4, p. 306 | 14, 15 |
| P7: about 80% plan-wide | Knopp et al. (2024), Key points p. 1 (78.8%) | 6 |
| G: 1.5 threshold | Zhou & Zhou (2025), §4.1.3 | 1 |
| G: weekly window, cold start, proportional cut | OWN DESIGN | – |
| G4, G5 | Proposal §3.7.2, §3.7.3 | – |
| S1: user-chosen day | Daniels (2022), Ch. 8 (gold plan notes), Ch. 13 (Phase IV notes), Ch. 16 (Table 16.2) | 38 |
| S1: Sunday fallback | Daniels (2022), Ch. 10 "Sample Weekly Plan" | 27 |
| S1: race-weekday default | OWN DESIGN | – |
| S2: ≥ 2 easy days between hard sessions | Daniels (2022), Ch. 16 (novice and 2Q plans) | 24 |
| S2: long-run spacing | OWN DESIGN | – |
| S3: easy runs ≥ 30 min | Daniels (2022), Ch. 4 "Training Suggestions" | 20 |
| S4: M/T/I/R limits | Daniels (2022), Ch. 4 (M, T, I, R sections) | 22 |
| S5, S7 | OWN DESIGN | – |
| S6: session-RPE load | Foster et al. (2001), Methods | 4 |
| Long-track sessions (run/walk, T reps, race-pace run, 4 × 5 min T about 5 days out) | Daniels (2022), Ch. 16, Table 16.2 | 31 |
| Short-track sessions | OWN DESIGN (direction supported by Campos et al. 2022, p. 311; Smyth et al. 2022, Fig. 1; Knopp et al. 2024, pp. 9, 11) | 28–30 |
| Missed-session priority (Component 3 hook) | Daniels (2022), Ch. 10 "Sample Weekly Plan" | 39 |

Not covered by the map (tagged `SOURCE: TBC` in config): the S1 slot pattern per
capacity, and the 5–9% weekly-increase benchmark that the brief attributes to Knopp
et al. (2024). The "S1: Sunday fallback" row has no matching rule in the brief, so it
is not implemented.

**Secondary only (never in the reference list):** Bosquet et al. (2007), Midgley et
al. (2007) and Boullosa et al. (2020), each cited as "as cited in Knopp et al. (2024)".

## References used by Component 2 (APA 7)

- Campos, Y., Casado, A., Vieira, J. G., Guimarães, M., Sant'Ana, L., Leitão, L., da Silva, S. F., Silva Marques de Azevedo, P. H., Vianna, J., & Domínguez, R. (2022). Training-intensity distribution on middle- and long-distance runners: A systematic review. *International Journal of Sports Medicine, 43*(4), 305–316. https://doi.org/10.1055/a-1559-3623
- Daniels, J. (2022). *Daniels' running formula* (4th ed.). Human Kinetics.
- Feely, C., Smyth, B., Caulfield, B., & Lawlor, A. (2023). Estimating the cost of training disruptions on marathon performance. *Frontiers in Sports and Active Living, 4*, Article 1096124. https://doi.org/10.3389/fspor.2022.1096124
- Foster, C., Florhaug, J. A., Franklin, J., Gottschall, L., Hrovatin, L. A., Parker, S., Doleshal, P., & Dodge, C. (2001). A new approach to monitoring exercise training. *Journal of Strength and Conditioning Research, 15*(1), 109–115.
- Goldberg, M., Le Mat, Y., Metra, M., de Sousa, T., Edouard, P., Millet, G. Y., Pairot de Fontenay, B., & Debarnot, U. (2025). Poor sleep quality is associated with an increased risk of running-related injuries: A prospective study of 339 runners over six months. *Scandinavian Journal of Medicine & Science in Sports, 35*(11), Article e70164. https://doi.org/10.1111/sms.70164
- Knopp, M., Appelhans, D., Schönfelder, M., Seiler, S., & Wackerhage, H. (2024). Quantitative analysis of 92 12-week sub-elite marathon training plans. *Sports Medicine – Open, 10*, Article 50. https://doi.org/10.1186/s40798-024-00717-5
- Plateau, C. R., Anthony, J., Clemes, S. A., & Stevinson, C. D. (2022). Prospective study of beginner running groups: Psychological predictors and outcomes of participation. *Behavioral Medicine*. Advance online publication. https://doi.org/10.1080/08964289.2022.2100865
- Relph, N., Taylor, S. L., Christian, D. L., Dey, P., & Owen, M. B. (2023). "Couch-to-5k or Couch to Ouch to Couch!?" Who takes part in beginner runner programmes in the UK and is non-completion linked to musculoskeletal injury? *International Journal of Environmental Research and Public Health, 20*(17), Article 6682. https://doi.org/10.3390/ijerph20176682
- Smyth, B., Lawlor, A., Berndsen, J., & Feely, C. (2022). Recommendations for marathon runners: On the application of recommender systems and machine learning to support recreational marathon runners. *User Modeling and User-Adapted Interaction, 32*, 787–838. https://doi.org/10.1007/s11257-021-09299-3
- Zhou, L., & Zhou, K. (2025). A reinforcement learning-enabled system for personalised sports training plan generation. *International Journal of Information and Communication Technology, 26*(50), 72–87. https://doi.org/10.1504/IJICT.2025.10075262
