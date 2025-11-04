# Project Plan

## 1. Data Consolidation
- Ingest `data/State_Opioid_Dispensing_Rates_2006_2018.csv` and `data/State Opioid Dispensing Rates.csv`.
- Standardize column names, remove national aggregate rows, harmonize state keys, and merge into a single 2006–2023 state-year panel.
- Export cleaned dispensing panel for downstream use.

## 2. PDMP Preprocessing
- Parse implementation, operation, and access dates from `data/20170828_PDMPDates_Data.csv`.
- Collapse `data/PDMP Reporting and Authorized Use Data 8.23.22.csv` into yearly state indicators aligned with the dispensing panel.
- Produce a unified PDMP feature table indexed by state and year.

## 3. High-Prescribing Adoption Definition
- Choose CDC-aligned high-rate thresholds (e.g., absolute cutoff or percentile).
- Flag `is_high` per state-year and record the first year each state enters the high category.
- Save adoption-year mapping for analysis.

## 4. Influence Network Construction
- For each year, add edges from states already high to states newly high in the subsequent year.
- Aggregate edge counts, optionally normalize by exposure opportunities, and prune weak edges.
- Bootstrap years to quantify uncertainty on edge weights.

## 5. Influential State Ranking
- Compute eigenvector, weighted degree, and betweenness centralities on the pruned network.
- Identify stable top-k states across sensitivity and bootstrap runs.
- Export rankings with uncertainty ranges.

## 6. Baseline Diffusion Replay
- Calibrate a propagation model using inferred edges to replay held-out years.
- Compare performance against a no-network carry-forward baseline and independent per-state models.
- Summarize forecast accuracy metrics.

## 7. Policy-Aligned Intervention Simulations
- Disable outgoing influence from selected top-k states starting at PDMP implementation or access years.
- Re-run simulations, capturing changes in yearly high-state counts versus the baseline.
- Report bootstrap confidence intervals for intervention impacts.

## 8. Evaluation and Reporting
- Document errors, ranking stability, and intervention outcomes with supporting figures and tables.
- Highlight PDMP coverage limits (post-2017) and non-causal interpretation of inferred influence.
- Integrate results, robustness checks, and policy discussion into the paper sections in `project.txt`.

