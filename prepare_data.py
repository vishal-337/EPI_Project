import os
import pandas as pd
import numpy as np

BASE = "/Users/vishal/Desktop/EPI_Project"
DATA = os.path.join(BASE, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(BASE, "outputs")
os.makedirs(PROC, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

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
cdc_early = cdc_early[cols]
cdc_late = cdc_late[cols]
cdc_all = pd.concat([cdc_early, cdc_late], ignore_index=True)
cdc_all = cdc_all.dropna(subset=["YEAR", "STATE_ABBREV", "opioid_dispensing_rate"]).copy()
cdc_all["YEAR"] = cdc_all["YEAR"].astype(int)
cdc_all = cdc_all.sort_values(["STATE_ABBREV", "YEAR"]).drop_duplicates(["STATE_ABBREV", "YEAR"], keep="last")
cdc_all.to_csv(os.path.join(PROC, "dispensing_state_year.csv"), index=False)

pdmp_dates = pd.read_csv(os.path.join(DATA, "20170828_PDMPDates_Data.csv"))
date_cols = [c for c in pdmp_dates.columns if c.startswith("pdmpimp-") or c in ["Jurisdictions"]]
pdmp_dates = pdmp_dates[date_cols].rename(columns={"Jurisdictions": "STATE_NAME"})
for c in pdmp_dates.columns:
    if c == "STATE_NAME":
        continue
    pdmp_dates[c] = pd.to_datetime(pdmp_dates[c], errors="coerce")
pdmp_years = pd.DataFrame({"STATE_NAME": pdmp_dates["STATE_NAME"]})
for c in pdmp_dates.columns:
    if c == "STATE_NAME":
        continue
    pdmp_years[c+"_year"] = pdmp_dates[c].dt.year
pdmp_years["STATE_ABBREV"] = pdmp_years["STATE_NAME"].map(dict(zip(cdc_all["STATE_NAME"], cdc_all["STATE_ABBREV"]))).fillna(pdmp_years["STATE_NAME"])
pdmp_years = pdmp_years.drop_duplicates("STATE_ABBREV")

pdmp_var = pd.read_csv(os.path.join(DATA, "PDMP Reporting and Authorized Use Data 8.23.22.csv"))
pdmp_var = pdmp_var.rename(columns={"Jurisdictions": "STATE_NAME"})
pdmp_var["Effective Date"] = pd.to_datetime(pdmp_var["Effective Date"], errors="coerce")
pdmp_var["Valid Through Date"] = pd.to_datetime(pdmp_var["Valid Through Date"], errors="coerce")
years = pd.Index(range(int(cdc_all["YEAR"].min()), int(cdc_all["YEAR"].max())+1), name="YEAR")
states = cdc_all[["STATE_NAME", "STATE_ABBREV"]].drop_duplicates()
state_year = states.assign(key=1).merge(pd.DataFrame({"YEAR": years, "key": 1}), on="key").drop(columns=["key"]) 

flag_cols = [c for c in pdmp_var.columns if c not in ["STATE_NAME", "Effective Date", "Valid Through Date"]]
for c in flag_cols:
    pdmp_var[c] = pd.to_numeric(pdmp_var[c], errors="coerce").fillna(0).astype(int)

rows = []
for _, r in pdmp_var.iterrows():
    s = r["STATE_NAME"]
    start = r["Effective Date"]
    end = r["Valid Through Date"]
    y0 = int(start.year) if pd.notnull(start) else None
    y1 = int(end.year) if pd.notnull(end) else None
    if y0 is None:
        continue
    ys = years if y1 is None else years[(years>=y0) & (years<=y1)]
    for y in ys:
        rows.append((s, int(y), r[flag_cols].values))

if len(rows) > 0:
    expanded = pd.DataFrame(rows, columns=["STATE_NAME", "YEAR", "vals"]) 
    flags = pd.DataFrame(expanded["vals"].tolist(), columns=flag_cols)
    expanded = pd.concat([expanded.drop(columns=["vals"]), flags], axis=1)
    pdmp_yearly = expanded.groupby(["STATE_NAME", "YEAR"], as_index=False)[flag_cols].max()
else:
    pdmp_yearly = state_year.copy()
    for c in flag_cols:
        pdmp_yearly[c] = 0

pdmp_yearly = pdmp_yearly.merge(states, on="STATE_NAME", how="left")
pdmp_yearly = pdmp_yearly[["YEAR", "STATE_NAME", "STATE_ABBREV"] + flag_cols]
pdmp_yearly.to_csv(os.path.join(PROC, "pdmp_yearly.csv"), index=False)

panel = cdc_all.merge(pdmp_yearly, on=["STATE_NAME", "STATE_ABBREV", "YEAR"], how="left")

thr = 51.7
panel["is_high"] = (panel["opioid_dispensing_rate"] > thr).astype(int)
panel = panel.sort_values(["STATE_ABBREV", "YEAR"]).reset_index(drop=True)
adoption = panel.groupby("STATE_ABBREV").apply(lambda df: df.loc[df["is_high"].diff().fillna(df["is_high"]).gt(0) | ((df["is_high"]==1) & (df["is_high"].shift(1).fillna(0)==0)), "YEAR"].min()).rename("adoption_year").reset_index()
adoption["adoption_year"] = adoption["adoption_year"].astype("Int64")
adoption = adoption.merge(panel[["STATE_ABBREV", "STATE_NAME"]].drop_duplicates(), on="STATE_ABBREV", how="left")
adoption = adoption[["STATE_NAME", "STATE_ABBREV", "adoption_year"]]
adoption.to_csv(os.path.join(PROC, "adoption_year.csv"), index=False)

panel = panel.merge(adoption[["STATE_ABBREV", "adoption_year"]], on="STATE_ABBREV", how="left")
panel.to_csv(os.path.join(PROC, "dispensing_with_flags.csv"), index=False)

edges = {}
years_sorted = sorted(panel["YEAR"].unique())
for t in years_sorted:
    if t+1 not in panel["YEAR"].values:
        continue
    a = panel[(panel["YEAR"] == t) & (panel["is_high"] == 1)]["STATE_ABBREV"].tolist()
    b_prev = panel[(panel["YEAR"] == t) & (panel["is_high"] == 0)]["STATE_ABBREV"].tolist()
    b_now = panel[(panel["YEAR"] == t+1) & (panel["is_high"] == 1)]["STATE_ABBREV"].tolist()
    b_new = set(b_now).intersection(set(b_prev))
    for src in a:
        for dst in b_new:
            if src == dst:
                continue
            edges[(src, dst)] = edges.get((src, dst), 0) + 1

edge_df = pd.DataFrame([(s, d, w) for (s, d), w in edges.items()], columns=["source", "target", "weight"]) if len(edges) else pd.DataFrame(columns=["source", "target", "weight"])
edge_df = edge_df.sort_values(["weight", "source", "target"], ascending=[False, True, True])
edge_df.to_csv(os.path.join(OUT, "influence_edges.csv"), index=False)


