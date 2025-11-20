import pandas as pd
import os

# Load the data
df = pd.read_csv("data/processed/dispensing_state_year.csv")

# Filter for the first year (2006)
df_2006 = df[df["YEAR"] == 2006]

print("=" * 60)
print("THRESHOLD ANALYSIS FOR OPIOID DISPENSING RATES")
print("=" * 60)

print("\n--- 2006 Opioid Dispensing Rate Statistics ---")
print(df_2006["opioid_dispensing_rate"].describe())

print("\n--- Percentiles ---")
print(f"50th percentile (Median): {df_2006['opioid_dispensing_rate'].median()}")
print(f"75th percentile: {df_2006['opioid_dispensing_rate'].quantile(0.75)}")
print(f"90th percentile: {df_2006['opioid_dispensing_rate'].quantile(0.90)}")

print("\n--- Current Threshold (51.7) ---")
above_thr = df_2006[df_2006["opioid_dispensing_rate"] > 51.7]
print(f"States above 51.7 in 2006: {len(above_thr)} out of {len(df_2006)}")

# Now let's test alternative thresholds across ALL years
thresholds = {
    "Current (51.7)": 51.7,
    "Median (77.5)": 77.5,
    "75th %ile (87.35)": 87.35,
    "90th %ile (108.7)": 108.7
}

print("\n" + "=" * 60)
print("ADOPTION DYNAMICS ACROSS ALL YEARS")
print("=" * 60)

for name, thr in thresholds.items():
    print(f"\n--- Threshold: {name} ---")
    df["is_high_temp"] = (df["opioid_dispensing_rate"] > thr).astype(int)
    
    years = sorted(df["YEAR"].unique())
    total_transitions = 0
    
    for year in years:
        if year + 1 not in df["YEAR"].values:
            continue
            
        cur = df[df["YEAR"] == year][["STATE_ABBREV", "is_high_temp"]].set_index("STATE_ABBREV")["is_high_temp"]
        nxt = df[df["YEAR"] == year + 1][["STATE_ABBREV", "is_high_temp"]].set_index("STATE_ABBREV")["is_high_temp"]
        
        common = cur.index.intersection(nxt.index)
        cur = cur.loc[common]
        nxt = nxt.loc[common]
        
        # Count high states in current year
        num_high = len(cur[cur == 1])
        
        # Count new adopters (0 -> 1 transitions)
        new_adopters = nxt[(nxt == 1) & (cur == 0)].index.tolist()
        
        if year == 2006:
            print(f"  {year}: {num_high} states already high")
        if new_adopters:
            print(f"  {year} -> {year+1}: {len(new_adopters)} new adopters {new_adopters}")
            total_transitions += len(new_adopters)
    
    print(f"  Total 0->1 transitions: {total_transitions}")
    
df.drop("is_high_temp", axis=1, inplace=True)
