# State-Level Opioid Dispensing Analysis: Results Summary

## Executive Summary

This analysis models the spatial diffusion of high opioid prescribing rates across US states (2006-2018) using influence networks and spatial autoregressive models. Key findings indicate that **geographic proximity is a significant predictor** of prescribing behavior, with Southern states acting as primary influencers in the epidemic's spread.

---

## 1. Data Overview

| Metric | Value |
|--------|-------|
| Time Period | 2006-2023 (analysis: 2006-2018) |
| States Analyzed | 50 + DC |
| High-Prescribing Threshold | 87.35 prescriptions per 100 persons (75th percentile) |
| States Ever Reaching "High" Status | 25 (49%) |

---

## 2. Adoption Dynamics

### 2.1 Temporal Pattern of High-Prescribing Adoption

| Year | New High-Prescribing States | Cumulative Total |
|------|----------------------------|------------------|
| 2006 | AL, AR, IN, KY, LA, MS, NV, OH, OK, OR, SC, TN, WV (13) | 13 |
| 2007 | DE, NC, UT (3) | 16 |
| 2008 | ME, MI (2) | 18 |
| 2009 | GA, MO (2) | 20 |
| 2010 | AZ, FL, ID (3) | 23 |
| 2011 | KS (1) | 24 |
| 2012 | MT (1) | 25 |

**Key Finding**: The epidemic showed rapid initial spread (13 states in 2006), followed by slower geographic diffusion through neighboring states. By 2012, all eventual high-prescribing states had adopted the behavior.

---

## 3. Influence Network Analysis

### 3.1 Network Statistics

| Metric | Value |
|--------|-------|
| Nodes (States in Network) | 20 |
| Edges (Influence Relationships) | 21 |
| Total Influence Weight | 10.03 |

### 3.2 Top Influential States (By Cumulative Out-Degree Weight)

| Rank | State | Out-Degree Weight | Interpretation |
|------|-------|-------------------|----------------|
| 1 | **Tennessee (TN)** | 1.67 | Highest outward influence |
| 2 | **Nevada (NV)** | 1.50 | Strong Western hub |
| 3 | **South Carolina (SC)** | 1.33 | Southeast spreader |
| 4 | **Georgia (GA)** | 1.00 | Regional bridge |
| 5 | **Alabama (AL)** | 0.58 | Southern contributor |

### 3.3 Most Susceptible States (By Incoming Influence)

| Rank | State | In-Degree Weight | Interpretation |
|------|-------|------------------|----------------|
| 1 | **North Carolina (NC)** | 2.00 | Most influenced by neighbors |
| 2 | **Georgia (GA)** | 1.50 | Dual role: influenced & influencer |
| 3 | **Missouri (MO)** | 1.33 | Central crossroads state |
| 4 | **Florida (FL)** | 1.25 | Southeast terminus |
| 5 | **Michigan (MI)** | 1.00 | Midwest adoption |

### 3.4 Key Influence Pathways

The strongest direct influence relationships (weight = 1.0):
- **GA → FL**: Georgia influenced Florida's adoption (2010)
- **NV → UT**: Nevada influenced Utah's adoption (2007)
- **SC → NC**: South Carolina influenced North Carolina (2007)
- **TN → NC**: Tennessee influenced North Carolina (2007)

---

## 4. Spatial Autoregressive Model Results

### 4.1 Model Specification

$$\text{Rate}_{s,t+1} = \alpha + \beta \cdot \text{Rate}_{s,t} + \gamma \cdot \overline{\text{Rate}}_{\text{neighbors},t} + \epsilon$$

### 4.2 Estimated Parameters

| Parameter | Estimate | Interpretation |
|-----------|----------|----------------|
| α (Intercept) | 0.18 | Baseline rate |
| **β (Self-Persistence)** | **0.981** | 98.1% of current rate persists |
| **γ (Spatial Spillover)** | **0.009** | Neighbor rates contribute ~1% |

### 4.3 Model Performance

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **R² Score** | **0.884** | Model explains 88.4% of variance |
| **MSE** | 21.58 | Average squared error |
| Training Samples | 510 | |
| Testing Samples | 306 | |

**Key Finding**: The extremely high self-persistence coefficient (β = 0.981) indicates that opioid prescribing rates are **highly path-dependent**—once a state reaches high rates, it tends to stay there. The spatial spillover effect (γ = 0.009), while statistically present, is small compared to self-persistence.

---

## 5. Diffusion Simulation Results

### 5.1 One-Step-Ahead Prediction Accuracy

| Year Transition | Actual New Adopters | Correct Predictions | Accuracy | vs Random Baseline |
|-----------------|---------------------|---------------------|----------|-------------------|
| 2006→2007 | 3 | 2 | **66.7%** | 23.7% |
| 2007→2008 | 2 | 0 | 0.0% | 11.4% |
| 2008→2009 | 2 | 2 | **100%** | 12.1% |
| 2009→2010 | 3 | 1 | 33.3% | 28.1% |
| 2010→2011 | 1 | 0 | 0.0% | 3.4% |
| 2011→2012 | 1 | 0 | 0.0% | 3.4% |

**Overall Accuracy**: 41.7% (5/12 correct predictions)

**Key Finding**: The network model performs **significantly better than random** in early years when geographic clustering is strong, but loses predictive power as remaining non-adopters become geographically isolated from the high-prescribing cluster.

---

## 6. Key Conclusions for Paper

### 6.1 Primary Findings

1. **Geographic Clustering**: High opioid prescribing rates are strongly clustered in the Southeast (TN, AL, SC, KY, WV) and parts of the Mountain West (NV, OR).

2. **Path Dependence**: The spatial autoregressive model confirms that prescribing behavior is highly persistent (β = 0.981). States that became high-prescribers in 2006 largely remained so throughout the study period.

3. **Limited but Measurable Spillover**: Neighbor state rates have a small but statistically detectable effect (γ = 0.009), supporting the hypothesis that prescribing norms diffuse across state borders.

4. **Tennessee as Primary Influencer**: TN had the highest outward influence, consistent with its early adoption, central location, and high prescribing rates.

### 6.2 Policy Implications

1. **Regional Interventions**: Given the geographic clustering, regional policy interventions (multi-state compacts) may be more effective than state-by-state approaches.

2. **Early Intervention Critical**: The high self-persistence means prevention of initial adoption is far more effective than attempting reversal.

3. **Border State Monitoring**: States bordering high-prescribing states should implement enhanced monitoring programs.

### 6.3 Model Limitations

1. **Geographic Constraint Assumption**: The model only allows influence between adjacent states, potentially missing long-range effects (e.g., policy imitation).

2. **Binary Threshold**: The "high-prescribing" classification simplifies a continuous spectrum of behavior.

3. **Confounding Factors**: The model does not account for state-level policy changes, demographic shifts, or economic factors.

---

## 7. Figures Generated

| Figure | Description | File |
|--------|-------------|------|
| Influence Network | Directed graph showing state-to-state influence | `influence_network_graph.png` |
| Top Influencers | Bar chart of states by out-degree weight | `top_influencers_bar.png` |
| Adoption Timeline | Cumulative adoption curve 2006-2012 | `historical_adoption_curve.png` |
| Prediction Scatter | Actual vs Predicted rates (R² = 0.884) | `continuous_prediction_scatter.png` |

---

## 8. Data Files Generated

| File | Description |
|------|-------------|
| `influence_edges.csv` | All 21 influence relationships with weights |
| `state_influence_rankings.csv` | Full centrality metrics for all states |
| `continuous_prediction_results.csv` | State-by-state predictions vs actuals |
| `simulation_results.csv` | Year-by-year diffusion prediction accuracy |

---

## 9. County-Level Analysis

### 9.1 Superspreader Counties

Counties that adopted high-prescribing behavior **before** their state crossed the threshold.

| Metric | Value |
|--------|-------|
| Total Superspreader Counties | 345 |
| States with Superspreaders | 12 |
| Maximum Years Early | 6 (Montana counties) |

**Top States by Superspreader Count:**

| Rank | State | Superspreader Counties |
|------|-------|------------------------|
| 1 | Georgia | 83 |
| 2 | North Carolina | 47 |
| 3 | Michigan | 42 |
| 4 | Florida | 41 |
| 5 | Missouri | 38 |

**Key Finding**: Montana counties were the earliest superspreaders (6 years before state adoption), followed by Kansas counties (5 years early). This suggests localized "hotspots" existed well before state-level epidemics emerged.

### 9.2 Intra-State Influence Network

Using state-specific 75th percentile thresholds to identify high-prescribing counties within each state:

| Metric | Value |
|--------|-------|
| Total Influence Edges | 26,180 |
| States with Networks | 50 |
| Total Counties Ranked | 1,597 |

**Top 10 Influential Counties (Weighted Out-Degree):**

| Rank | County | State | Influence Score |
|------|--------|-------|-----------------|
| 1 | Bowie County | TX | 29.23 |
| 2 | Gregg County | TX | 29.23 |
| 3 | Wichita County | TX | 29.17 |
| 4 | Taylor County | TX | 29.10 |
| 5 | Limestone County | TX | 29.03 |
| 6 | Palo Pinto County | TX | 29.03 |
| 7 | Brown County | TX | 29.03 |
| 8 | Gray County | TX | 29.03 |
| 9 | Grayson County | TX | 29.03 |
| 10 | Hardin County | TX | 29.03 |

**Key Finding**: Texas counties dominate the top influencer list despite Texas not being a "high-prescribing state" nationally. This reflects the intra-state relative threshold approach—these counties were early and persistent high-prescribers *within Texas*.

**Total Influence by State:**

| Rank | State | Cumulative Influence Score |
|------|-------|---------------------------|
| 1 | Texas | 2,311.35 |
| 2 | Kentucky | 793.24 |
| 3 | Georgia | 723.74 |
| 4 | Tennessee | 660.23 |
| 5 | Indiana | 484.11 |

### 9.3 County-Level Spatial Autoregressive Model

**Model Specification:**
$$\text{CountyRate}_{c,t+1} = \alpha + \beta \cdot \text{CountyRate}_{c,t} + \gamma \cdot \text{StateRate}_{s,t} + \epsilon$$

**Estimated Parameters (All Counties):**

| Parameter | Estimate | Interpretation |
|-----------|----------|----------------|
| α (Intercept) | -0.63 | Baseline adjustment |
| **β (County Self-Persistence)** | **0.950** | 95% persistence at county level |
| **γ (State Context Effect)** | **0.050** | 5% influence from state average |

**Model Performance:**

| Metric | All Counties | Georgia Only |
|--------|--------------|--------------|
| **R²** | **0.792** | **0.783** |
| **MSE** | 211.37 | 296.53 |
| Training Samples | 30,867 | 1,520 |
| Testing Samples | 18,157 | 923 |

**Georgia-Specific Coefficients:**

| Parameter | GA Estimate | Interpretation |
|-----------|-------------|----------------|
| α (Intercept) | -23.26 | Lower baseline in GA |
| β (County Self-Persistence) | 0.968 | Higher persistence |
| γ (State Context Effect) | 0.315 | **Stronger state influence (31.5%)** |

**Key Finding**: The Georgia model shows significantly higher state-level influence (γ = 0.315 vs 0.050), suggesting that within Georgia, state-level trends have a stronger effect on county behavior than in the national model. This could reflect Georgia's centralized healthcare policies or regional clustering effects.

### 9.4 Comparison: State vs County Models

| Aspect | State-Level | County-Level |
|--------|-------------|--------------|
| Self-Persistence (β) | 0.981 | 0.950 |
| Spatial Spillover (γ) | 0.009 | 0.050 |
| R² | 0.884 | 0.792 |

**Interpretation**: County-level prescribing shows slightly less persistence and stronger spatial effects, consistent with greater variability at finer geographic scales.

---

## 10. County-Level Figures Generated

| Figure | Description | File |
|--------|-------------|------|
| County Influencers | Bar chart of top 10 influential counties | `top_influential_counties.png` |
| County Prediction | Actual vs Predicted scatter plot | `county_prediction_scatter.png` |
| Georgia Prediction | GA-specific scatter plot | `ga_county_prediction_scatter.png` |

---

## 11. County-Level Data Files

| File | Description |
|------|-------------|
| `county_influence_edges.csv` | 26,180 intra-state influence relationships |
| `county_influence_rankings.csv` | 1,597 counties ranked by influence |
| `county_superspreaders.csv` | 345 superspreader counties |
| `county_prediction_results.csv` | All county predictions vs actuals |
| `ga_county_prediction_results.csv` | Georgia-specific predictions |

---

*Analysis conducted: December 2, 2025*
*Data source: CDC Opioid Dispensing Rates, 2006-2023*
