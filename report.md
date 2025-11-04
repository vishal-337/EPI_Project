# Project Milestone Report

## Title
Modeling the Opioid Prescription Epidemic as a Clinical Practice Contagion

## 1. Introduction and Scope
This milestone report documents approximately thirty percent progress toward a final project that aims to model the spread of high opioid prescribing as a diffusion process across U.S. states. We ask whether sustained “high prescribing” tends to appear in a temporally ordered pattern consistent with influence, rather than as independent, unrelated events. We build a directed, time‑ordered influence network from state dispensing rates; prepare policy timelines for counterfactual simulations; and set out evaluation, robustness, and ethical guardrails. The present draft is intentionally complete in narrative and methodology but does not yet include major results such as rankings or intervention effects.

### 1.1 Problem Statement and Hypotheses
We consider each state as an entity that can transition from non‑high to high opioid prescribing under a CDC‑aligned threshold. Our primary hypothesis is temporal precedence: when a state is already high at time y, states that become high at time y+1 are plausibly influenced by the prior high environment. A secondary hypothesis is concentration: a small set of states serve historically as repeat sources of exposure for later adopters. A tertiary hypothesis is policy alignment: PDMP milestones create natural boundaries for when influence could plausibly have been reduced.

### 1.2 Project Status and Contributions
We have consolidated and cleaned state‑year dispensing data (2006–2023), constructed PDMP features from legal datasets, defined “high prescribing” using the CDC’s >51.7 category boundary, computed first‑adoption years, generated timing‑based influence edges, and produced a first visualization. Code is scripted and reproducible. Remaining work includes ranking, baseline replay, policy‑timed interventions, and robustness studies.

## 2. Related Work
Network diffusion, influence inference from adoption times, and public‑health network analyses inform this project. Classical diffusion models such as Independent Cascade and Linear Threshold formalize mechanisms through which behaviors spread, and they establish that selecting seed sets to maximize expected adoption is NP‑hard yet approximately solvable by greedy methods under submodularity. These results provide conceptual justification for evaluating influential states via centrality and for considering diminishing returns when multiple sources target the same destinations.

Inverse inference methods such as NETINF show how one can recover latent edges from observed infection times when many cascades unfold on a fixed graph. While our setting differs—one macro‑level cascade observed annually rather than thousands of independent memes—the intuition that timing differentials encode directional information still holds. Public‑health applications, including prescriber‑patient networks and supra‑dyadic clustering in risky‑prescribing behaviors, demonstrate that influence is structured and that geography is an imperfect proxy for the true pathways along which practices propagate. These literatures motivate building an explicit, directed network at the state level before evaluating targeting or simulating interventions. We adopt their logic while simplifying the statistical machinery to emphasize transparency and policy readability.

## 3. Data and Collection Process
Our outcome series is CDC’s state‑level opioid prescriptions dispensed per 100 persons. We merged two official CSVs: a historical panel covering 2006–2018 and a current series covering 2019–2023. Both files include YEAR, state identifiers, and a continuous dispensing rate; the 2019+ series also lists categorical bins, with an explicit top category of >51.7. We aligned schema, removed national aggregates, harmonized DC, coerced types, and deduplicated by state‑year to yield `data/processed/dispensing_state_year.csv`.

For policy timing, we used PDAPS legal datasets. The PDMP Dates table encodes enactment, operation, and access milestones per state. The Reporting and Authorized Use table provides time‑varying policy flags with effective and valid‑through dates (e.g., mandatory access, reciprocity rules, reportable schedules). We parsed both, expanded date ranges to annual indicators, and aligned to state keys, producing `data/processed/pdmp_yearly.csv`. Current coverage extends to 2017, which constrains the latest intervention start years we will model without additional sources.

Data processing is performed by scripts colocated with the project and designed to auto‑discover paths relative to the script location, ensuring portability across machines without hardcoded absolute roots.

## 4. Initial Findings and Summary Statistics
We summarize the consolidated panel and engineered variables to provide intuition prior to modeling.

### 4.1 Coverage and Completeness
The merged CDC panel spans 2006–2023 for 50 states and DC, resulting in a dense time‑series matrix with few missing rates. PDMP coverage spans earlier years through 2017; we successfully mapped all states in the dates file and the majority of time‑varying policy rows into annual flags.

### 4.2 Thresholding and Adoptions
Using τ = 51.7, we computed `is_high` per state‑year and the first‑adoption year for each state. High status is more prevalent in earlier years, consistent with the national decline reported by CDC since 2012. Adoption years cluster before the mid‑2010s, with a smaller tail of late adopters near and after 2017–2020.

### 4.3 First‑Pass Network Pattern
The year‑ahead handoff rule creates edges from every state that is already high at y to any state that becomes newly high at y+1. Because a state only newly adopts once, most edges have weight one. The diagnostic graph reveals a dense pattern of arrows converging on late adopters and diffuse arrows emanating from earlier high states.

These patterns motivate robustness exercises for the final report: widening the exposure window to account for slower diffusion, normalizing by the number of available sources, and pruning low‑support edges for readability.

## 5. Mathematical Background
Let S be the set of states and Y the set of calendar years. Let r(s,y) denote the opioid dispensing rate in prescriptions per 100 persons. Define τ as the high‑prescribing threshold; in this work τ = 51.7, aligned to CDC categories. Define the high set at year y: H_y = {s ∈ S : r(s,y) > τ}. Define a state’s adoption year as a(s) = min{y ∈ Y : s ∈ H_y}, if it ever becomes high.

We interpret temporal precedence using set differences of successive years. A state v that is in H_{y+1} but not in H_y is considered a new adopter at y+1. Any state u ∈ H_y is considered an available source at time y. The cross‑product Sy × Ny+1 induces directed edges (u,v) with unit increment in weight for that year. Summing over y produces the weighted directed graph G = (S,E,w).

The approach captures order information but not causation; time‑coincident national shocks can generate edges even absent direct influence. The graph can be analyzed with centrality measures on directed weighted graphs. Eigenvector centrality x satisfies x = λ A x for adjacency A, adapted for weights; out‑degree and betweenness provide additional views. Simulations treat incoming weighted edges as exposure intensities that raise the probability of adoption for susceptible states.

## 6. Formal Description of Implemented Algorithms

### 6.1 CDC Consolidation
Inputs: historical CSV (2006–2018), current CSV (2019–2023). Process: normalize headers; remove national rows; coerce numeric; concatenate; sort by (STATE_ABBREV, YEAR); drop duplicates keeping last. Output: `dispensing_state_year.csv`.

### 6.2 PDMP Yearly Expansion
Inputs: PDMP Dates and Reporting/Authorized Use CSVs. Process: parse dates; map `Jurisdictions` to state names; expand [effective, valid‑through] to integer years; coerce non‑date fields to integers; for each state‑year, take max across overlapping segments. Output: `pdmp_yearly.csv`.

### 6.3 Thresholding and Adoption
Inputs: `dispensing_state_year.csv`. Process: set τ=51.7; compute `is_high = 1[r>τ]`; define adoption year for each state as earliest year with `is_high=1`. Outputs: `dispensing_with_is_high.csv`, `adoption_year.csv`.

### 6.4 Influence Edge Construction
Inputs: `dispensing_with_is_high.csv`. For each y with y+1 present, construct sources Sy = H_y and new adopters Ny+1 = H_{y+1} \ H_y. For each u ∈ Sy and v ∈ Ny+1, increment w(u,v) by 1. Aggregate across y and write `influence_edges.csv`. A visualization script lays out the graph with node size proportional to out‑strength and edge width proportional to weight, saving `influence_network.png`.

## 7. General Difficulties and Design Choices

### 7.1 Single‑Cascade Evidence
Unlike settings with thousands of cascades, we observe one macro cascade measured annually. This limits statistical power for edge inference. Our design emphasizes transparency and robustness rather than likelihood‑based reconstruction. We will report sensitivity to exposure windows and thresholds and provide uncertainty bands from bootstrap over years.

### 7.2 Threshold Selection
Thresholds change conclusions. A percentile‑based threshold adapts to early‑era dispersion but complicates interpretation. The CDC category boundary offers clarity and external validity. We therefore adopt τ=51.7 for the main analysis, reporting sensitivity to alternative cutoffs in the final.

### 7.3 Window Length and Opportunity
Strict y→y+1 edges compress influence into single‑year transitions. Many practice shifts likely require multi‑year exposure. We will test k‑year windows and normalize by |Sy| to mitigate spurious edges created by large source sets.

### 7.4 Policy Data Truncation
PDMP features stop in 2017 in the available files. Simulations that extend beyond 2017 will be clearly caveated. If time permits, we will source newer PDAPS or state repositories to extend coverage.

### 7.5 Interpretability and Ethics
We avoid attributing blame. Network findings will be framed as decision support about systems and timing, not as causal attribution to states or clinicians. Assumptions and limitations will be documented alongside each result.

## 8. What Remains and Plan for Final Version

### 8.1 Centrality and Influential Sets
Compute eigenvector, degree, and betweenness centralities on the weighted digraph; summarize top‑k sets and their stability across thresholds, windows, and pruning cutoffs. Report uncertainty intervals via bootstrap.

### 8.2 Baselines and Replay Accuracy
Implement a no‑network carry‑forward baseline and an independent per‑state model; train on early years and evaluate held‑out overlap and error. Compare against network‑based replay.

### 8.3 PDMP‑Aligned Interventions
Select top‑k states; set their outgoing influence to zero from PDMP operation or access years onward; re‑simulate adoption trajectories; measure differences versus baseline with uncertainty bands.

### 8.4 Robustness Suite
Vary τ, k‑year window length, opportunity normalization, and pruning thresholds; summarize where conclusions are stable and where they change.

### 8.5 Reporting and Packaging
Produce figures for network, centrality bars, baseline vs. observed, and intervention deltas. Provide a reproducibility section listing exact commands to regenerate artifacts from raw data.

## 9. Engineering, Reproducibility, and Artifacts
All code is scripted with path autodiscovery relative to file location. The data flow is linear and easily rerunnable:
- `Data Pre-Processing/cdc_preprocess.py` → `data/processed/dispensing_state_year.csv`
- `Data Pre-Processing/pdmp_preprocess.py` → `data/processed/pdmp_yearly.csv`
- `compute_adoption.py` → `data/processed/dispensing_with_is_high.csv`, `data/processed/adoption_year.csv`
- `build_influence_network.py` → `outputs/influence_edges.csv`
- `visualize_influence.py` → `outputs/influence_network.png`

The repository organizes raw inputs in `data/`, engineered panels in `data/processed/`, and figures/edge lists in `outputs/`.

## 10. Conclusion
This milestone delivers a complete, reproducible foundation: cleaned data, a transparent adoption definition, and a first‑pass influence network. The remaining work focuses on ranking, baselines, intervention simulations, and robustness. The final report will present quantitative results, ablations, and policy‑aligned interpretations grounded in the limitations described above.

