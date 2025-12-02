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
    # 1. Load Datasets
    cdc_early = pd.read_csv(os.path.join(DATA, "State_Opioid_Dispensing_Rates_2006_2018.csv"))
    cdc_late = pd.read_csv(os.path.join(DATA, "State Opioid Dispensing Rates.csv"))

    # 2. Clean Early Data (2006-2018)
    # Rename column to standard name
    cdc_early = cdc_early.rename(columns={"Opioid Dispensing Rate (per 100 persons)": "opioid_dispensing_rate_dup"})
    # Drop duplicate columns if they exist
    cdc_early = cdc_early.drop(columns=[c for c in ["opioid_dispensing_rate_dup"] if c in cdc_early.columns])
    cdc_early = cdc_early[cdc_early["STATE_NAME"] != "United States"]
    cdc_early["opioid_dispensing_rate"] = pd.to_numeric(cdc_early["opioid_dispensing_rate"], errors="coerce")

    # 3. Clean Late Data (2019-2020+)
    cdc_late = cdc_late.rename(columns={"Opioid Dispensing Rate (per 100 persons)": "rate_bin"})
    cdc_late = cdc_late[cdc_late["STATE_NAME"] != "United States"]
    cdc_late["opioid_dispensing_rate"] = pd.to_numeric(cdc_late["opioid_dispensing_rate"], errors="coerce")

    # 4. Merge
    cols = ["YEAR", "STATE_NAME", "STATE_ABBREV", "STATE_FIPS", "opioid_dispensing_rate"]
    
    # Ensure columns exist
    for df in [cdc_early, cdc_late]:
        for c in cols:
            if c not in df.columns:
                print(f"Warning: Column {c} missing in dataset")

    cdc_early = cdc_early[cols]
    cdc_late = cdc_late[cols]
    
    cdc_all = pd.concat([cdc_early, cdc_late], ignore_index=True)
    
    # 5. Final Cleanup
    cdc_all = cdc_all.dropna(subset=["YEAR", "STATE_ABBREV", "opioid_dispensing_rate"]).copy()
    cdc_all["YEAR"] = cdc_all["YEAR"].astype(int)
    
    # Remove duplicates (keep last updated value)
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
    
    # 1. Clean Rate Column
    # Convert "Data unavailable" and other non-numeric strings to NaN
    df["opioid_dispensing_rate"] = pd.to_numeric(df["opioid_dispensing_rate"], errors="coerce")
    
    # 2. Clean FIPS Codes
    # Ensure FIPS are 5-digit strings (e.g., 2013 -> "02013")
    # Handle potential float/int issues by converting to int first if possible, then str
    # Some FIPS might be read as floats (e.g. 2013.0)
    df["STATE_COUNTY_FIP_U"] = pd.to_numeric(df["STATE_COUNTY_FIP_U"], errors='coerce').fillna(0).astype(int)
    df["FIPS"] = df["STATE_COUNTY_FIP_U"].astype(str).str.zfill(5)
    
    # 3. Select and Rename Columns
    # We need: YEAR, STATE_ABBREV, COUNTY_NAME, FIPS, opioid_dispensing_rate
    cols = ["YEAR", "STATE_ABBREV", "COUNTY_NAME", "FIPS", "opioid_dispensing_rate"]
    
    # Check if columns exist
    missing_cols = [c for c in cols if c not in df.columns and c != "FIPS"]
    if missing_cols:
        print(f"Warning: Missing columns in county data: {missing_cols}")
    
    df = df[cols]
    
    # 4. Drop Missing Data
    initial_len = len(df)
    df = df.dropna(subset=["opioid_dispensing_rate", "FIPS", "YEAR"])
    dropped_len = initial_len - len(df)
    if dropped_len > 0:
        print(f"Dropped {dropped_len} rows with missing dispensing rates or FIPS.")

    # 5. Sort and Save
    df["YEAR"] = df["YEAR"].astype(int)
    df = df.sort_values(["FIPS", "YEAR"])
    
    out_path = os.path.join(PROC, "dispensing_county_year.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved processed county data to {out_path}")

if __name__ == "__main__":
    process_state_data()
    process_county_data()


