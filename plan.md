# Project Plan

## 1. Data Consolidation
- **State Level:** Ingest `data/State_Opioid_Dispensing_Rates_2006_2018.csv` and `data/State Opioid Dispensing Rates.csv`. Merge into a single 2006–2023 state-year panel.
- **County Level:** Ingest `data/County Opioid Dispensing Rates_Complete.csv`. Clean FIPS codes, standardize names, and create a county-year panel.
- **Output:** `dispensing_state_year.csv` and `dispensing_county_year.csv`.

## 2. High-Prescribing Adoption Definition
- **State Level:** Define "High-Prescribing" using a global 75th percentile threshold. Flag `is_high` and record adoption years.
- **County Level:** Define "High-Prescribing" using **state-specific** 75th percentile thresholds to account for regional baselines.
- **Super-Spreaders:** Identify counties that adopted high rates significantly earlier than their state average.

## 3. Influence Network Construction
- **State Network:** Construct edges based on **Geographic Adjacency** combined with **Temporal Decay** (states high in year $t$ -> neighbors becoming high in $t+1$).
- **County Network:** Construct **Intra-State** influence networks. Connect counties within the same state based on temporal precedence of high-prescribing status.

## 4. Influential Node Ranking
- **State Level:** Compute centrality metrics (Weighted Out-Degree, Eigenvector, Betweenness) to identify national influencers.
- **County Level:** Compute centrality metrics (Weighted Out-Degree, Eigenvector) within state networks to identify local drivers.

## 5. Continuous Prediction Models
- **State Level:** Implement a **Spatial Autoregressive Model** to predict continuous dispensing rates.
    - Features: Self-history (Autoregression) + Neighboring state averages (Spatial Spillover).
- **County Level:** Implement a continuous regression model.
    - Features: County's own history + State-level trends.
- **Case Study:** Perform a focused prediction analysis for **Georgia (GA)** counties to validate the model at a granular level.

## 6. Evaluation and Reporting
- **Visualizations:**
    - Network graphs and centrality rankings.
    - "Super-Spreader" county timelines.
    - Actual vs. Predicted scatter plots for model validation.
- **Metrics:** Evaluate models using $R^2$ and MSE.
- **Analysis:** Discuss the "Montana Anomaly" (local hotspots preceding state trends) and the strong state-county coupling in Georgia.

