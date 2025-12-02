import os
import pandas as pd
import numpy as np

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
DATA = os.path.join(PROJECT_ROOT, "data", "raw")
PROC = os.path.join(PROJECT_ROOT, "data", "processed")
os.makedirs(PROC, exist_ok=True)

def process_state_data():
    print("Processing State Data...")
    cdc_early = pd.read_csv(os.path.join(DATA, "State_Opioid_Dispensing_Rates_2006_2018.csv"))
    cdc_late = pd.read_csv(os.path.join(DATA, "State Opioid Dispensing Rates.csv"))

    cdc_early = cdc_early.rename(columns={"Opioid Dispensing Rate (per 100 persons)": "opioid_dispensing_rate_dup"})
    cdc_early = cdc_early.drop(columns=[c for c in ["opioid_dispensing_rate_dup"] if c in cdc_early.columns])
    cdc_early = cdc_early[cdc_early["STATE_NAME"] != "United States"]
    cdc_early["opioid_dispensing_rate"] = pd.to_numeric(cdc_early["opioid_dispensing_rate"], errors="coerce")

    cdc_late = cdc_late.rename(columns={"Opioid Dispensing Rate (per 100 persons)": "rate_bin"})
    cdc_late = cdc_late[cdc_late["STATE_NAME"] != "United States"]
    cdc_late["opioid_dispensing_rate"] = pd.to_numeric(cdc_late["opioid_dispensing_rate"], errors="coerce")

    cols = ["YEAR", "STATE_NAME", "STATE_ABBREV", "STATE_FIPS", "opioid_dispensing_rate"]
    
    for df in [cdc_early, cdc_late]:
        for c in cols:
            if c not in df.columns:
                print(f"Warning: Column {c} missing in dataset")

    cdc_early = cdc_early[cols]
    cdc_late = cdc_late[cols]
    
    cdc_all = pd.concat([cdc_early, cdc_late], ignore_index=True)
    
    cdc_all = cdc_all.dropna(subset=["YEAR", "STATE_ABBREV", "opioid_dispensing_rate"]).copy()
    cdc_all["YEAR"] = cdc_all["YEAR"].astype(int)
    
    cdc_all = cdc_all.sort_values(["STATE_ABBREV", "YEAR"]).drop_duplicates(["STATE_ABBREV", "YEAR"], keep="last")
    
    out_path = os.path.join(PROC, "dispensing_state_year.csv")
    cdc_all.to_csv(out_path, index=False)
    print(f"Saved merged state data to {out_path}")

def process_county_data():
    print("Processing County Data...")
    county_path = os.path.join(DATA, "County Opioid Dispensing Rates_Complete.csv")
    
    if not os.path.exists(county_path):
        print(f"Error: County data file not found at {county_path}")
        return

    df = pd.read_csv(county_path)
    
    df["opioid_dispensing_rate"] = pd.to_numeric(df["opioid_dispensing_rate"], errors="coerce")
    
    df["STATE_COUNTY_FIP_U"] = pd.to_numeric(df["STATE_COUNTY_FIP_U"], errors='coerce').fillna(0).astype(int)
    df["FIPS"] = df["STATE_COUNTY_FIP_U"].astype(str).str.zfill(5)
    
    cols = ["YEAR", "STATE_ABBREV", "COUNTY_NAME", "FIPS", "opioid_dispensing_rate"]
    
    missing_cols = [c for c in cols if c not in df.columns and c != "FIPS"]
    if missing_cols:
        print(f"Warning: Missing columns in county data: {missing_cols}")
    
    df = df[cols]
    
    initial_len = len(df)
    df = df.dropna(subset=["opioid_dispensing_rate", "FIPS", "YEAR"])
    dropped_len = initial_len - len(df)
    if dropped_len > 0:
        print(f"Dropped {dropped_len} rows with missing dispensing rates or FIPS.")

    df["YEAR"] = df["YEAR"].astype(int)
    df = df.sort_values(["FIPS", "YEAR"])
    
    out_path = os.path.join(PROC, "dispensing_county_year.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved processed county data to {out_path}")

if __name__ == "__main__":
    process_state_data()
    process_county_data()


