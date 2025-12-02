import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
DATA = os.path.join(PROJECT_ROOT, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

# --- Geographic Adjacency Dictionary (Same as build_influence_network.py) ---
NEIGHBORS = {
    'AL': ['FL', 'GA', 'MS', 'TN'],
    'AK': [],
    'AZ': ['CA', 'CO', 'NV', 'NM', 'UT'],
    'AR': ['LA', 'MS', 'MO', 'OK', 'TN', 'TX'],
    'CA': ['AZ', 'NV', 'OR'],
    'CO': ['AZ', 'KS', 'NE', 'NM', 'OK', 'UT', 'WY'],
    'CT': ['MA', 'NY', 'RI'],
    'DE': ['MD', 'NJ', 'PA'],
    'FL': ['AL', 'GA'],
    'GA': ['AL', 'FL', 'NC', 'SC', 'TN'],
    'HI': [],
    'ID': ['MT', 'NV', 'OR', 'UT', 'WA', 'WY'],
    'IL': ['IN', 'IA', 'KY', 'MO', 'WI'],
    'IN': ['IL', 'KY', 'MI', 'OH'],
    'IA': ['IL', 'MN', 'MO', 'NE', 'SD', 'WI'],
    'KS': ['CO', 'MO', 'NE', 'OK'],
    'KY': ['IL', 'IN', 'MO', 'OH', 'TN', 'VA', 'WV'],
    'LA': ['AR', 'MS', 'TX'],
    'ME': ['NH'],
    'MD': ['DE', 'PA', 'VA', 'WV'],
    'MA': ['CT', 'NH', 'NY', 'RI', 'VT'],
    'MI': ['IN', 'OH', 'WI'],
    'MN': ['IA', 'ND', 'SD', 'WI'],
    'MS': ['AL', 'AR', 'LA', 'TN'],
    'MO': ['AR', 'IL', 'IA', 'KS', 'KY', 'NE', 'OK', 'TN'],
    'MT': ['ID', 'ND', 'SD', 'WY'],
    'NE': ['CO', 'IA', 'KS', 'MO', 'SD', 'WY'],
    'NV': ['AZ', 'CA', 'ID', 'OR', 'UT'],
    'NH': ['ME', 'MA', 'VT'],
    'NJ': ['DE', 'NY', 'PA'],
    'NM': ['AZ', 'CO', 'OK', 'TX', 'UT'],
    'NY': ['CT', 'MA', 'NJ', 'PA', 'VT'],
    'NC': ['GA', 'SC', 'TN', 'VA'],
    'ND': ['MN', 'MT', 'SD'],
    'OH': ['IN', 'KY', 'MI', 'PA', 'WV'],
    'OK': ['AR', 'CO', 'KS', 'MO', 'NM', 'TX'],
    'OR': ['CA', 'ID', 'NV', 'WA'],
    'PA': ['DE', 'MD', 'NJ', 'NY', 'OH', 'WV'],
    'RI': ['CT', 'MA'],
    'SC': ['GA', 'NC'],
    'SD': ['IA', 'MN', 'MT', 'NE', 'ND', 'WY'],
    'TN': ['AL', 'AR', 'GA', 'KY', 'MS', 'MO', 'NC', 'VA'],
    'TX': ['AR', 'LA', 'NM', 'OK'],
    'UT': ['AZ', 'CO', 'ID', 'NV', 'NM', 'WY'],
    'VT': ['MA', 'NH', 'NY'],
    'VA': ['KY', 'MD', 'NC', 'TN', 'WV'],
    'WA': ['ID', 'OR'],
    'WV': ['KY', 'MD', 'OH', 'PA', 'VA'],
    'WI': ['IL', 'IA', 'MI', 'MN'],
    'WY': ['CO', 'ID', 'MT', 'NE', 'SD', 'UT'],
    'DC': ['MD', 'VA']
}

def prepare_regression_data(df):
    """
    Constructs the feature matrix for the Spatial Autoregressive Model.
    Target: Rate(t+1)
    Features: 
      - Rate(t) (Autoregression)
      - Mean_Neighbor_Rate(t) (Spatial Influence)
    """
    X = []
    y = []
    meta = [] # Stores (Year, State) for tracking

    states = df["STATE_ABBREV"].unique()
    years = sorted(df["YEAR"].unique())

    # Create a lookup dictionary for fast access: rate_map[year][state] = rate
    rate_map = {}
    for yr in years:
        rate_map[yr] = df[df["YEAR"] == yr].set_index("STATE_ABBREV")["opioid_dispensing_rate"].to_dict()

    for t in years[:-1]: # Can't predict for the last year
        for s in states:
            if s not in rate_map[t] or s not in rate_map[t+1]:
                continue
            
            # Target: Next Year's Rate
            target_val = rate_map[t+1][s]
            
            # Feature 1: Current Rate (Self-History)
            current_val = rate_map[t][s]
            
            # Feature 2: Spatial Influence (Average of Neighbors)
            neighbors = NEIGHBORS.get(s, [])
            neighbor_vals = [rate_map[t][n] for n in neighbors if n in rate_map[t]]
            
            if len(neighbor_vals) > 0:
                spatial_val = np.mean(neighbor_vals)
            else:
                spatial_val = 0 # Isolated states like AK, HI
            
            X.append([current_val, spatial_val])
            y.append(target_val)
            meta.append((t+1, s))

    return np.array(X), np.array(y), meta

def main():
    print("Loading Data...")
    df = pd.read_csv(os.path.join(PROC, "dispensing_state_year.csv"))
    
    # Split into Train (2006-2016) and Test (2017-2020)
    # Note: We predict t+1, so training on 2006-2016 means predicting 2007-2017
    train_df = df[df["YEAR"] <= 2016]
    test_df = df[df["YEAR"] > 2016] # This will be used to validate predictions for 2017+
    
    print("Preparing Regression Matrices...")
    X_train, y_train, meta_train = prepare_regression_data(train_df)
    
    # For testing, we need the full dataset to look back at previous years
    # But we only evaluate on the test years
    X_full, y_full, meta_full = prepare_regression_data(df)
    
    # Filter test set based on meta_full years
    test_indices = [i for i, (yr, st) in enumerate(meta_full) if yr > 2017]
    X_test = X_full[test_indices]
    y_test = y_full[test_indices]
    meta_test = [meta_full[i] for i in test_indices]

    print(f"Training Samples: {len(X_train)}")
    print(f"Testing Samples: {len(X_test)}")

    # --- Model Training ---
    print("Training Spatial Autoregressive Model...")
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Coefficients
    beta_self = model.coef_[0]
    beta_spatial = model.coef_[1]
    intercept = model.intercept_
    
    print("\n" + "="*40)
    print("MODEL RESULTS")
    print("="*40)
    print(f"Equation: Rate(t+1) = {intercept:.2f} + {beta_self:.3f} * Rate(t) + {beta_spatial:.3f} * Neighbor_Rate(t)")
    print("-" * 40)
    print(f"Interpretation:")
    print(f" - Self-Persistence (Beta): {beta_self:.3f} (Strong history dependence)")
    print(f" - Spatial Influence (Gamma): {beta_spatial:.3f} (Spillover effect from neighbors)")
    
    # --- Evaluation ---
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print("-" * 40)
    print(f"Test MSE: {mse:.2f}")
    print(f"Test R2 Score: {r2:.3f}")
    print("="*40)

    # --- Save Predictions ---
    results = []
    for i, (yr, st) in enumerate(meta_test):
        results.append({
            "YEAR": yr,
            "STATE_ABBREV": st,
            "Actual_Rate": y_test[i],
            "Predicted_Rate": y_pred[i],
            "Error": y_test[i] - y_pred[i]
        })
    
    res_df = pd.DataFrame(results)
    res_path = os.path.join(OUT, "continuous_prediction_results.csv")
    res_df.to_csv(res_path, index=False)
    print(f"\nDetailed predictions saved to {res_path}")

    # --- Visualization ---
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5, color='blue')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel("Actual Dispensing Rate")
    plt.ylabel("Predicted Dispensing Rate")
    plt.title(f"Spatial Autoregressive Model: Actual vs Predicted (R2={r2:.2f})")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "continuous_prediction_scatter.png"), dpi=300)
    print(f"Scatter plot saved to {os.path.join(OUT, 'continuous_prediction_scatter.png')}")

if __name__ == "__main__":
    main()
