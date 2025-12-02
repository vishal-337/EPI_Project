import os
import pandas as pd
import numpy as np

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
DATA = os.path.join(PROJECT_ROOT, "data")
PROC = os.path.join(DATA, "processed")
os.makedirs(PROC, exist_ok=True)

src = os.path.join(PROC, "dispensing_state_year.csv")
df = pd.read_csv(src)
df = df.dropna(subset=["YEAR", "STATE_ABBREV", "opioid_dispensing_rate"]).copy()
df["YEAR"] = df["YEAR"].astype(int)

thr = 87.35

df = df.sort_values(["STATE_ABBREV", "YEAR"]).reset_index(drop=True)
df["is_high"] = (df["opioid_dispensing_rate"] > thr).astype(int)

adoption = (
    df[df["is_high"] == 1]
    .groupby("STATE_ABBREV", as_index=False)["YEAR"].min()
    .rename(columns={"YEAR": "adoption_year"})
)
adoption = adoption.merge(df[["STATE_ABBREV", "STATE_NAME"]].drop_duplicates(), on="STATE_ABBREV", how="left")
adoption = adoption[["STATE_NAME", "STATE_ABBREV", "adoption_year"]]

df_out = df.copy()
df_out.to_csv(os.path.join(PROC, "dispensing_with_is_high.csv"), index=False)
adoption.to_csv(os.path.join(PROC, "adoption_year.csv"), index=False)


