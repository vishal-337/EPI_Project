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

def main():
    print("Loading Data...")
    county_path = os.path.join(PROC, "dispensing_county_year.csv")
    state_path = os.path.join(PROC, "dispensing_state_year.csv")
    
    if not os.path.exists(county_path) or not os.path.exists(state_path):
        print("Missing data files.")
        return

    df_county = pd.read_csv(county_path)
    df_state = pd.read_csv(state_path)
    
    df_state = df_state[["YEAR", "STATE_ABBREV", "opioid_dispensing_rate"]].rename(
        columns={"opioid_dispensing_rate": "state_rate"}
    )
    
    df = df_county.merge(df_state, on=["YEAR", "STATE_ABBREV"], how="left")
    
    df = df.sort_values(["FIPS", "YEAR"])
    
    df["target_next_year"] = df.groupby("FIPS")["opioid_dispensing_rate"].shift(-1)
    
    df_model = df.dropna(subset=["target_next_year", "opioid_dispensing_rate", "state_rate"])
    
    X = df_model[["opioid_dispensing_rate", "state_rate"]]
    y = df_model["target_next_year"]
    
    train_mask = df_model["YEAR"] <= 2016
    test_mask = df_model["YEAR"] > 2016
    
    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    
    print(f"Training Samples: {len(X_train)}")
    print(f"Testing Samples: {len(X_test)}")
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    print("\nModel Coefficients:")
    print(f"Intercept: {model.intercept_:.2f}")
    print(f"County Rate (t) Coeff: {model.coef_[0]:.3f}")
    print(f"State Rate (t) Coeff: {model.coef_[1]:.3f}")
    
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    
    print(f"\nTest R2: {r2:.3f}")
    print(f"Test MSE: {mse:.2f}")
    
    results = df_model[test_mask].copy()
    results["predicted_rate"] = y_pred
    results["error"] = results["target_next_year"] - results["predicted_rate"]
    
    res_path = os.path.join(OUT, "county_prediction_results.csv")
    results.to_csv(res_path, index=False)
    print(f"Saved predictions to {res_path}")
    
    plt.figure(figsize=(10, 6))
    if len(y_test) > 5000:
        indices = np.random.choice(len(y_test), 5000, replace=False)
        plt.scatter(y_test.iloc[indices], y_pred[indices], alpha=0.1, s=10)
    else:
        plt.scatter(y_test, y_pred, alpha=0.1, s=10)
        
    plt.plot([0, y_test.max()], [0, y_test.max()], 'r--')
    plt.xlabel("Actual Rate (t+1)")
    plt.ylabel("Predicted Rate (t+1)")
    plt.title(f"County Level Prediction (R2={r2:.2f})")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "county_prediction_scatter.png"))

if __name__ == "__main__":
    main()