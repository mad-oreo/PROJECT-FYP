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
4. **Sourced vs. original.** Don't dress up Naji's own design (membership functions,
   rule base, conflict-resolution ordering, rep structures, easing polarity, K
   gain) as literature-derived.
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
| `Estimating_the_cost_of_training_disruptions_on_marathon_performance.md` | *(verify)* | Training-disruption cost (motivates adjustment) | **[VERIFY]** |
| `Physiology_and_Pathophysiology.md` | *(verify)* | Physiological grounding | **[VERIFY]** |
| `Systematic_review_..._decision_fatigue...md` | *(verify)* | Decision-fatigue review (motivation for automation) | **[VERIFY]** |
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
