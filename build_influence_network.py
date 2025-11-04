import os
import argparse
import pandas as pd

ROOT = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.join(ROOT, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("--min_support", type=int, default=1)
args = parser.parse_args()

panel = pd.read_csv(os.path.join(PROC, "dispensing_with_is_high.csv"))
panel = panel[["YEAR", "STATE_ABBREV", "is_high"]].dropna()
panel["YEAR"] = panel["YEAR"].astype(int)
panel["is_high"] = panel["is_high"].astype(int)

years = sorted(panel["YEAR"].unique())
edge_counts = {}
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
            edge_counts[(s, d)] = edge_counts.get((s, d), 0) + 1

edges = pd.DataFrame([(s, d, w) for (s, d), w in edge_counts.items()], columns=["source", "target", "weight"]).sort_values(["weight", "source", "target"], ascending=[False, True, True])
edges.to_csv(os.path.join(OUT, "influence_edges.csv"), index=False)

if args.min_support > 1 and not edges.empty:
    pruned = edges[edges["weight"] >= args.min_support].reset_index(drop=True)
    pruned.to_csv(os.path.join(OUT, "influence_edges_pruned.csv"), index=False)


