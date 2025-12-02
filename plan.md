# Project Plan

## 1. Data Consolidation
- **State Level:** Ingest `data/State_Opioid_Dispensing_Rates_2006_2018.csv` and `data/State Opioid Dispensing Rates.csv`. Merge into a single 2006–2023 state-year panel.
- **County Level:** Ingest `data/County Opioid Dispensing Rates_Complete.csv`. Clean FIPS codes, standardize names, and create a county-year panel.
- Export cleaned panels for downstream use.

## 2. High-Prescribing Adoption Definition
- Define "High-Prescribing" thresholds for both State and County levels (e.g., top decile, absolute CDC thresholds).
- Flag `is_high` per state-year and county-year.
- Record the "adoption year" (first year entering high status) for each entity.

## 3. Influence Network Construction
- **State Network:** Construct edges based on temporal precedence (states high in year $t$ -> states becoming high in $t+1$).
- **County Network:** Construct edges similarly, potentially constrained by geographic adjacency or within-state relationships to manage the larger scale.
- Prune weak edges and bootstrap to quantify edge stability.

## 4. Influential Node Ranking
- Compute centrality metrics (eigenvector, PageRank) for the State network.
- Compute centrality metrics for the County network to identify "super-spreader" counties.
- Export rankings of the most influential states and counties.

## 5. Network-Based Prediction and Validation
- Split data into training (early years) and testing (later years) sets.
- Train network influence models on the training set for both State and County levels.
- Predict the dispensing rates or "high" status for the test set.
- Compare network-based prediction accuracy against non-network baselines (e.g., ARIMA, simple carry-forward).

## 6. Evaluation and Reporting
- Visualize the inferred influence networks (State and County).
- Report prediction accuracy metrics (RMSE, Accuracy, F1-score).
- Discuss the stability of rankings and the predictive power of the network approach.
- Integrate results into the final paper structure.

