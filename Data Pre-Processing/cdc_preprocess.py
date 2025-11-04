import os
import pandas as pd
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
PROC = os.path.join(DATA, "processed")
os.makedirs(PROC, exist_ok=True)

early_path = os.path.join(DATA, "State_Opioid_Dispensing_Rates_2006_2018.csv")
late_path = os.path.join(DATA, "State Opioid Dispensing Rates.csv")

cdc_early = pd.read_csv(early_path)
cdc_late = pd.read_csv(late_path)

cdc_early = cdc_early.rename(columns={"Opioid Dispensing Rate (per 100 persons)": "dup"})
cdc_early = cdc_early.drop(columns=[c for c in ["dup"] if c in cdc_early.columns])
cdc_early = cdc_early[cdc_early["STATE_NAME"] != "United States"]
cdc_early["opioid_dispensing_rate"] = pd.to_numeric(cdc_early["opioid_dispensing_rate"], errors="coerce")

cdc_late = cdc_late.rename(columns={"Opioid Dispensing Rate (per 100 persons)": "rate_bin"})
cdc_late = cdc_late[cdc_late["STATE_NAME"] != "United States"]
cdc_late["opioid_dispensing_rate"] = pd.to_numeric(cdc_late["opioid_dispensing_rate"], errors="coerce")

cols = ["YEAR", "STATE_NAME", "STATE_ABBREV", "STATE_FIPS", "opioid_dispensing_rate"]
cdc_early = cdc_early[cols]
cdc_late = cdc_late[cols]
cdc_all = pd.concat([cdc_early, cdc_late], ignore_index=True)
cdc_all = cdc_all.dropna(subset=["YEAR", "STATE_ABBREV", "opioid_dispensing_rate"]).copy()
cdc_all["YEAR"] = cdc_all["YEAR"].astype(int)
cdc_all = cdc_all.sort_values(["STATE_ABBREV", "YEAR"]).drop_duplicates(["STATE_ABBREV", "YEAR"], keep="last")
cdc_all.to_csv(os.path.join(PROC, "dispensing_state_year.csv"), index=False)


