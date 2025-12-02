import os
import pandas as pd
import numpy as np

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
DATA = os.path.join(PROJECT_ROOT, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

def main():
    print("Building Intra-State County Networks...")
    
    df = pd.read_csv(os.path.join(PROC, "dispensing_county_year.csv"))
    
    # REMOVED: Global threshold calculation
    # threshold = df["opioid_dispensing_rate"].quantile(0.75)
    # df["is_high"] = (df["opioid_dispensing_rate"] > threshold).astype(int)
    # adoption = df[df["is_high"] == 1].groupby(["STATE_ABBREV", "FIPS"])["YEAR"].min().to_dict()
    
    all_edges = []
    
    states = df["STATE_ABBREV"].unique()
    print(f"Processing {len(states)} states individually...")
    
    for state in states:
        # 1. Filter for specific state
        state_df = df[df["STATE_ABBREV"] == state].copy()
        
        if state_df.empty:
            continue
            
        # 2. Calculate State-Specific Threshold (75th percentile)
        local_threshold = state_df["opioid_dispensing_rate"].quantile(0.75)
        
        # 3. Define High Status relative to THIS state
        state_df["is_high"] = (state_df["opioid_dispensing_rate"] > local_threshold).astype(int)
        
        # 4. Calculate Adoption Years for this state's counties
        local_adoption = state_df[state_df["is_high"] == 1].groupby("FIPS")["YEAR"].min().to_dict()
        
        years = sorted(state_df["YEAR"].unique())
        
        edge_counts = {}
        
        for t in years[:-1]:
            cur_data = state_df[state_df["YEAR"] == t].set_index("FIPS")["is_high"]
            nxt_data = state_df[state_df["YEAR"] == t+1].set_index("FIPS")["is_high"]
            
            common = cur_data.index.intersection(nxt_data.index)
            cur = cur_data.loc[common]
            nxt = nxt_data.loc[common]
            
            sources = cur[cur == 1].index.tolist()
            targets = nxt[(nxt == 1) & (cur == 0)].index.tolist()
            
            if not sources or not targets:
                continue
                
            for s in sources:
                for d in targets:
                    if s == d: continue
                    
                    # Use local adoption map
                    s_adopt = local_adoption.get(s, t)
                    time_diff = max(0, t - s_adopt)
                    weight = 1.0 / (1.0 + time_diff)
                    
                    edge_counts[(s, d)] = edge_counts.get((s, d), 0.0) + weight
        
        for (s, d), w in edge_counts.items():
            all_edges.append({
                "STATE_ABBREV": state,
                "source_fips": s,
                "target_fips": d,
                "weight": w
            })
            
    edges_df = pd.DataFrame(all_edges)
    
    # Add names
    fips_map = df[["FIPS", "COUNTY_NAME"]].drop_duplicates().set_index("FIPS")["COUNTY_NAME"].to_dict()
    edges_df["source_name"] = edges_df["source_fips"].map(fips_map)
    edges_df["target_name"] = edges_df["target_fips"].map(fips_map)
    
    edges_df = edges_df.sort_values(["STATE_ABBREV", "weight"], ascending=[True, False])
    
    out_path = os.path.join(OUT, "county_influence_edges.csv")
    edges_df.to_csv(out_path, index=False)
    print(f"Saved {len(edges_df)} edges to {out_path}")

if __name__ == "__main__":
    main()