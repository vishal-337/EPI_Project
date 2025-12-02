================================================================================
                        Opioid Epidemic Network Modeling
================================================================================


INSTALLATION
------------
Requires Python 3.8+

Install dependencies:
    pip install pandas numpy scikit-learn networkx matplotlib


HOW TO USE
----------
All scripts are in the src/ folder. Run them in order:

1. PREPROCESS DATA
   python src/preprocessing/prepare_data.py

2. STATE-LEVEL ANALYSIS
   python src/state_level/compute_adoption.py
   python src/state_level/build_influence_network.py
   python src/state_level/rank_influencers.py
   python src/state_level/predict_continuous.py

3. COUNTY-LEVEL ANALYSIS
   python src/county_level/build_intra_state_networks.py
   python src/county_level/find_superspreaders.py
   python src/county_level/rank_county_influencers.py
   python src/county_level/predict_county_continuous.py
   python src/county_level/visualize_state_networks.py

4. VISUALIZATIONS
   python src/visualization/create_visualizations.py
   python src/visualization/paper_visualizations.py


QUICK DEMO
----------
To run the full pipeline:

    cd EPI_Project
    
    # Preprocess
    python src/preprocessing/prepare_data.py
    
    # State analysis
    python src/state_level/compute_adoption.py
    python src/state_level/build_influence_network.py
    python src/state_level/rank_influencers.py
    python src/state_level/predict_continuous.py
    
    # County analysis
    python src/county_level/build_intra_state_networks.py
    python src/county_level/find_superspreaders.py
    python src/county_level/rank_county_influencers.py
    python src/county_level/visualize_state_networks.py

Results are saved to outputs/ folder:
  - CSV files with rankings and predictions
  - PNG visualizations of networks and model performance
  - state_networks/ subfolder with per-state network graphs


OUTPUT FILES
------------
State-Level:
  - influence_edges.csv          State-to-state influence relationships
  - state_influence_rankings.csv State centrality scores
  - continuous_prediction_results.csv  Model predictions (R²=0.884)

County-Level:
  - county_influence_edges.csv   Intra-state county influence
  - county_top10_by_state.csv    Top 10 influential counties per state
  - county_superspreaders.csv    Counties that adopted before their state
  - state_networks/*.png         Network graph for each state


KEY FINDINGS
------------
  - 25 states became "high-prescribing" (>87.35 per 100 persons) by 2012
  - Tennessee, Nevada, South Carolina were top state-level influencers
  - Texas counties dominate county-level influence rankings
  - State-level model: R²=0.884, 98% self-persistence, 1% neighbor spillover
  - County-level model: R²=0.792, 95% self-persistence, 5% state context


For detailed results, see RESULTS_SUMMARY.md
================================================================================
