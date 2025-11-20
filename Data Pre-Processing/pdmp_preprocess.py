import os
import pandas as pd
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
PROC = os.path.join(DATA, "processed")
os.makedirs(PROC, exist_ok=True)

dates_path = os.path.join(DATA, "20170828_PDMPDates_Data.csv")
var_path = os.path.join(DATA, "PDMP Reporting and Authorized Use Data 8.23.22.csv")

pdmp_dates = pd.read_csv(dates_path)
pdmp_dates = pdmp_dates[[c for c in pdmp_dates.columns if c.startswith("pdmpimp-") or c == "Jurisdictions"]]
pdmp_dates = pdmp_dates.rename(columns={"Jurisdictions": "STATE_NAME"})
for c in pdmp_dates.columns:
    if c == "STATE_NAME":
        continue
    pdmp_dates[c] = pd.to_datetime(pdmp_dates[c], errors="coerce")
pdmp_years = pd.DataFrame({"STATE_NAME": pdmp_dates["STATE_NAME"]})
for c in pdmp_dates.columns:
    if c == "STATE_NAME":
        continue
    pdmp_years[c+"_year"] = pdmp_dates[c].dt.year

try:
    cdc_any = pd.read_csv(os.path.join(DATA, "State_Opioid_Dispensing_Rates_2006_2018.csv"))[["STATE_NAME", "STATE_ABBREV"]].drop_duplicates()
except Exception:
    cdc_any = pd.DataFrame(columns=["STATE_NAME", "STATE_ABBREV"])
pdmp_years = pdmp_years.merge(cdc_any, on="STATE_NAME", how="left")
pdmp_years = pdmp_years.drop_duplicates("STATE_NAME")

pdmp_var = pd.read_csv(var_path)
pdmp_var = pdmp_var.rename(columns={"Jurisdictions": "STATE_NAME"})
pdmp_var["Effective Date"] = pd.to_datetime(pdmp_var["Effective Date"], errors="coerce")
pdmp_var["Valid Through Date"] = pd.to_datetime(pdmp_var["Valid Through Date"], errors="coerce")

# FIX 1: The dataset is cut off at 2016-07-01. We assume policies active then are still active.
cutoff_date = pd.Timestamp("2016-07-01")
pdmp_var.loc[pdmp_var["Valid Through Date"] == cutoff_date, "Valid Through Date"] = pd.NaT

flag_cols = [c for c in pdmp_var.columns if c not in ["STATE_NAME", "Effective Date", "Valid Through Date"]]
for c in flag_cols:
    pdmp_var[c] = pd.to_numeric(pdmp_var[c], errors="coerce").fillna(0).astype(int)

years_all = list(range(1990, 2030))
rows = []
for _, r in pdmp_var.iterrows():
    s = r["STATE_NAME"]
    start = r["Effective Date"]
    end = r["Valid Through Date"]
    y0 = int(start.year) if pd.notnull(start) else None
    y1 = int(end.year) if pd.notnull(end) else None
    
    if y0 is None:
        continue
        
    # FIX 2: Correctly handle open-ended policies (y1 is None) by respecting the start year (y0)
    if y1 is None:
        ys = [y for y in years_all if y >= y0]
    else:
        ys = [y for y in years_all if y >= y0 and y <= y1]
        
    for y in ys:
        rows.append((s, y, r[flag_cols].values))

if len(rows) > 0:
    expanded = pd.DataFrame(rows, columns=["STATE_NAME", "YEAR", "vals"]) 
    flags = pd.DataFrame(expanded["vals"].tolist(), columns=flag_cols)
    expanded = pd.concat([expanded.drop(columns=["vals"]), flags], axis=1)
    pdmp_yearly = expanded.groupby(["STATE_NAME", "YEAR"], as_index=False)[flag_cols].max()
else:
    pdmp_yearly = pd.DataFrame(columns=["STATE_NAME", "YEAR"] + flag_cols)

pdmp_yearly = pdmp_yearly.merge(cdc_any, on="STATE_NAME", how="left")
pdmp_yearly = pdmp_yearly[["YEAR", "STATE_NAME", "STATE_ABBREV"] + flag_cols]
pdmp_yearly.to_csv(os.path.join(PROC, "pdmp_yearly.csv"), index=False)


