# EPI_Project: Opioid Dispensing Rate Analysis

An epidemiological analysis of opioid dispensing patterns across US states and counties, modeling influence networks and predicting prescription rates.

## Project Structure

```
EPI_Project/
├── README.md                    # This file
├── plan.md                      # Project plan and methodology
├── analysis_report.md           # Analysis findings and results
├── data/
│   ├── raw/                     # Original CDC data files
│   │   ├── State_Opioid_Dispensing_Rates_2006_2018.csv
│   │   ├── State Opioid Dispensing Rates.csv
│   │   └── County Opioid Dispensing Rates_Complete.csv
│   └── processed/               # Cleaned and transformed data
│       ├── dispensing_state_year.csv
│       ├── dispensing_county_year.csv
│       ├── dispensing_with_is_high.csv
│       └── adoption_year.csv
├── src/
│   ├── preprocessing/           # Data preparation
│   │   └── prepare_data.py      # Merges and cleans raw data
│   ├── state_level/             # State-level analysis
│   │   ├── compute_adoption.py  # Defines "high-prescribing" threshold
│   │   ├── build_influence_network.py  # Constructs state influence graph
│   │   ├── rank_influencers.py  # Computes centrality metrics
│   │   └── predict_continuous.py  # Spatial autoregressive model
│   ├── county_level/            # County-level analysis
│   │   ├── build_intra_state_networks.py  # Intra-state county networks
│   │   ├── find_superspreaders.py  # Identifies early-adopter counties
│   │   ├── rank_county_influencers.py  # County centrality metrics
│   │   ├── predict_county_continuous.py  # County prediction model
│   │   └── predict_ga_county.py  # Georgia case study
│   └── visualization/           # Plotting and charts
│       ├── create_visualizations.py  # Network graphs and rankings
│       └── visualize_superspreaders.py  # Superspreader visualizations
└── outputs/                     # Generated results and figures
    ├── *.csv                    # Analysis results
    └── *.png                    # Visualization outputs
```

## Pipeline Execution Order

### 1. Data Preprocessing
```bash
python src/preprocessing/prepare_data.py
```

### 2. State-Level Analysis
```bash
python src/state_level/compute_adoption.py
python src/state_level/build_influence_network.py
python src/state_level/rank_influencers.py
python src/state_level/predict_continuous.py
python src/state_level/simulate_diffusion.py
```

### 3. County-Level Analysis
```bash
python src/county_level/build_intra_state_networks.py
python src/county_level/find_superspreaders.py
python src/county_level/rank_county_influencers.py
python src/county_level/predict_county_continuous.py
python src/county_level/predict_ga_county.py
```

### 4. Visualizations
```bash
python src/visualization/create_visualizations.py
python src/visualization/visualize_superspreaders.py
```

## Key Concepts

- **High-Prescribing Threshold**: States above the 75th percentile (87.35 prescriptions per 100 persons)
- **Influence Network**: Geographic adjacency + temporal decay modeling
- **Super-Spreaders**: Counties adopting high rates significantly before their state average
- **Spatial Autoregression**: Predicting rates using self-history and neighbor averages

## Requirements

- Python 3.8+
- pandas, numpy, scikit-learn, networkx, matplotlib
