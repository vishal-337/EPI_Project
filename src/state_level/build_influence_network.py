import os
import argparse
import pandas as pd
import numpy as np

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
DATA = os.path.join(PROJECT_ROOT, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

NEIGHBORS = {
    'AL': ['FL', 'GA', 'MS', 'TN'],
    'AK': [],
    'AZ': ['CA', 'CO', 'NV', 'NM', 'UT'],
    'AR': ['LA', 'MS', 'MO', 'OK', 'TN', 'TX'],
    'CA': ['AZ', 'NV', 'OR'],
    'CO': ['AZ', 'KS', 'NE', 'NM', 'OK', 'UT', 'WY'],
    'CT': ['MA', 'NY', 'RI'],
    'DE': ['MD', 'NJ', 'PA'],
    'FL': ['AL', 'GA'],
    'GA': ['AL', 'FL', 'NC', 'SC', 'TN'],
    'HI': [],
    'ID': ['MT', 'NV', 'OR', 'UT', 'WA', 'WY'],
    'IL': ['IN', 'IA', 'KY', 'MO', 'WI'],
    'IN': ['IL', 'KY', 'MI', 'OH'],
    'IA': ['IL', 'MN', 'MO', 'NE', 'SD', 'WI'],
    'KS': ['CO', 'MO', 'NE', 'OK'],
    'KY': ['IL', 'IN', 'MO', 'OH', 'TN', 'VA', 'WV'],
    'LA': ['AR', 'MS', 'TX'],
    'ME': ['NH'],
    'MD': ['DE', 'PA', 'VA', 'WV'],
    'MA': ['CT', 'NH', 'NY', 'RI', 'VT'],
    'MI': ['IN', 'OH', 'WI'],
    'MN': ['IA', 'ND', 'SD', 'WI'],
    'MS': ['AL', 'AR', 'LA', 'TN'],
    'MO': ['AR', 'IL', 'IA', 'KS', 'KY', 'NE', 'OK', 'TN'],
    'MT': ['ID', 'ND', 'SD', 'WY'],
    'NE': ['CO', 'IA', 'KS', 'MO', 'SD', 'WY'],
    'NV': ['AZ', 'CA', 'ID', 'OR', 'UT'],
    'NH': ['ME', 'MA', 'VT'],
    'NJ': ['DE', 'NY', 'PA'],
    'NM': ['AZ', 'CO', 'OK', 'TX', 'UT'],
    'NY': ['CT', 'MA', 'NJ', 'PA', 'VT'],
    'NC': ['GA', 'SC', 'TN', 'VA'],
    'ND': ['MN', 'MT', 'SD'],
    'OH': ['IN', 'KY', 'MI', 'PA', 'WV'],
    'OK': ['AR', 'CO', 'KS', 'MO', 'NM', 'TX'],
    'OR': ['CA', 'ID', 'NV', 'WA'],
    'PA': ['DE', 'MD', 'NJ', 'NY', 'OH', 'WV'],
    'RI': ['CT', 'MA'],
    'SC': ['GA', 'NC'],
    'SD': ['IA', 'MN', 'MT', 'NE', 'ND', 'WY'],
    'TN': ['AL', 'AR', 'GA', 'KY', 'MS', 'MO', 'NC', 'VA'],
    'TX': ['AR', 'LA', 'NM', 'OK'],
    'UT': ['AZ', 'CO', 'ID', 'NV', 'NM', 'WY'],
    'VT': ['MA', 'NH', 'NY'],
    'VA': ['KY', 'MD', 'NC', 'TN', 'WV'],
    'WA': ['ID', 'OR'],
    'WV': ['KY', 'MD', 'OH', 'PA', 'VA'],
    'WI': ['IL', 'IA', 'MI', 'MN'],
    'WY': ['CO', 'ID', 'MT', 'NE', 'SD', 'UT'],
    'DC': ['MD', 'VA'] # Adding DC just in case
}

parser = argparse.ArgumentParser()
parser.add_argument("--min_support", type=float, default=0.0)
args = parser.parse_args()

panel = pd.read_csv(os.path.join(PROC, "dispensing_with_is_high.csv"))
panel = panel[["YEAR", "STATE_ABBREV", "is_high"]].dropna()
panel["YEAR"] = panel["YEAR"].astype(int)
panel["is_high"] = panel["is_high"].astype(int)

adoption_df = pd.read_csv(os.path.join(PROC, "adoption_year.csv"))
adoption_map = dict(zip(adoption_df["STATE_ABBREV"], adoption_df["adoption_year"]))

years = sorted(panel["YEAR"].unique())
edge_counts = {}

print("Building network with Geographic Constraints and Temporal Decay...")

for t in years:
    if (t + 1) not in panel["YEAR"].values:
        continue
    cur = panel[panel["YEAR"] == t][["STATE_ABBREV", "is_high"]].set_index("STATE_ABBREV")["is_high"]
    nxt = panel[panel["YEAR"] == (t + 1)][["STATE_ABBREV", "is_high"]].set_index("STATE_ABBREV")["is_high"]
    common = cur.index.intersection(nxt.index)
    cur = cur.loc[common]
    nxt = nxt.loc[common]
    
    sources = cur[cur == 1].index.tolist()
    new_adopters = nxt[(nxt == 1) & (cur == 0)].index.tolist()
    
    for s in sources:
        for d in new_adopters:
            if s == d:
                continue
            
            if d not in NEIGHBORS.get(s, []):
                continue
                
            s_adopt_year = adoption_map.get(s, t)
            time_diff = t - s_adopt_year
            if time_diff < 0: time_diff = 0
            
            decay_weight = 1.0 / (1.0 + time_diff)
            
            edge_counts[(s, d)] = edge_counts.get((s, d), 0.0) + decay_weight

edges = pd.DataFrame([(s, d, w) for (s, d), w in edge_counts.items()], columns=["source", "target", "weight"]).sort_values(["weight", "source", "target"], ascending=[False, True, True])
edges.to_csv(os.path.join(OUT, "influence_edges.csv"), index=False)

print("-" * 40)
print("INFLUENCE NETWORK ANALYTICS")
print("-" * 40)

if edges.empty:
    print("No edges found. This means no state transitioned from Low (0) to High (1) while other states were High.")
else:
    print(f"Total Edges Created: {len(edges)}")
    print(f"Total Weight (Influence Events): {edges['weight'].sum()}")
    
    print("\nTop 5 Influential Sources (Most Outgoing Influence):")
    top_sources = edges.groupby("source")["weight"].sum().sort_values(ascending=False).head(5)
    print(top_sources)

    print("\nTop 5 Susceptible Targets (Most Incoming Influence):")
    top_targets = edges.groupby("target")["weight"].sum().sort_values(ascending=False).head(5)
    print(top_targets)

    print("\nEdge Weight Distribution (How often pairs repeat):")
    print(edges["weight"].value_counts().sort_index())

    print("\nAdoption Events (0 -> 1 transitions) driving the network:")
    for t in years:
        if (t + 1) not in panel["YEAR"].values:
            continue
        cur = panel[panel["YEAR"] == t][["STATE_ABBREV", "is_high"]].set_index("STATE_ABBREV")["is_high"]
        nxt = panel[panel["YEAR"] == (t + 1)][["STATE_ABBREV", "is_high"]].set_index("STATE_ABBREV")["is_high"]
        
        common = cur.index.intersection(nxt.index)
        cur = cur.loc[common]
        nxt = nxt.loc[common]
        
        new_adopters = nxt[(nxt == 1) & (cur == 0)].index.tolist()
        
        if new_adopters:
            num_sources = len(cur[cur == 1])
            print(f"  {t} -> {t+1}: {len(new_adopters)} new adopters {new_adopters} (influenced by {num_sources} existing high states)")

print("-" * 40)

if args.min_support > 1 and not edges.empty:
    pruned = edges[edges["weight"] >= args.min_support].reset_index(drop=True)
    pruned.to_csv(os.path.join(OUT, "influence_edges_pruned.csv"), index=False)
    print(f"\nPruned network (min_support={args.min_support}) saved with {len(pruned)} edges.")


