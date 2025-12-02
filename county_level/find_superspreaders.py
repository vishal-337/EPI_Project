import os
import pandas as pd

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
DATA = os.path.join(PROJECT_ROOT, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

def main():
    county_path = os.path.join(PROC, "dispensing_county_year.csv")
    state_adopt_path = os.path.join(PROC, "adoption_year.csv")
    
    if not os.path.exists(county_path) or not os.path.exists(state_adopt_path):
        return

    df_county = pd.read_csv(county_path)
    df_state_adopt = pd.read_csv(state_adopt_path)

    THRESHOLD = 87.35

    high_counties = df_county[df_county["opioid_dispensing_rate"] > THRESHOLD].copy()
    
    county_adopt = high_counties.groupby(["FIPS", "COUNTY_NAME", "STATE_ABBREV"], as_index=False)["YEAR"].min()
    county_adopt = county_adopt.rename(columns={"YEAR": "county_adoption_year"})

    merged = county_adopt.merge(df_state_adopt[["STATE_ABBREV", "adoption_year"]], on="STATE_ABBREV", how="left")
    merged = merged.rename(columns={"adoption_year": "state_adoption_year"})

    superspreaders = merged[merged["county_adoption_year"] < merged["state_adoption_year"]].copy()
    superspreaders["years_early"] = superspreaders["state_adoption_year"] - superspreaders["county_adoption_year"]
    
    superspreaders = superspreaders.sort_values("years_early", ascending=False)

    out_path = os.path.join(OUT, "county_superspreaders.csv")
    superspreaders.to_csv(out_path, index=False)

if __name__ == "__main__":
    main()