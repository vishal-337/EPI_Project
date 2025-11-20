import os
import pandas as pd
import networkx as nx
import random

ROOT = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.join(ROOT, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(ROOT, "outputs")

edges_path = os.path.join(OUT, "influence_edges.csv")
panel_path = os.path.join(PROC, "dispensing_with_is_high.csv")

edges = pd.read_csv(edges_path)
panel = pd.read_csv(panel_path)

G = nx.DiGraph()
max_w = edges["weight"].max()
for _, r in edges.iterrows():
    G.add_edge(r["source"], r["target"], weight=r["weight"] / max_w)

years = sorted(panel["YEAR"].unique())
start_year = years[0]
initial_states = panel[(panel["YEAR"] == start_year) & (panel["is_high"] == 1)]["STATE_ABBREV"].tolist()

results = []
n_simulations = 100

for sim in range(n_simulations):
    active = set(initial_states)
    history = {start_year: len(active)}
    
    for year in years[1:]:
        newly_active = set()
        for node in active:
            if node not in G:
                continue
            for neighbor in G.successors(node):
                if neighbor not in active:
                    prob = G[node][neighbor]["weight"] * 0.5
                    if random.random() < prob:
                        newly_active.add(neighbor)
        
        active.update(newly_active)
        history[year] = len(active)
    
    for y, count in history.items():
        results.append({"simulation": sim, "year": y, "high_count": count})

res_df = pd.DataFrame(results)
avg_res = res_df.groupby("year")["high_count"].mean().reset_index()
avg_res.to_csv(os.path.join(OUT, "baseline_simulation_results.csv"), index=False)
print("Simulation results saved to outputs/baseline_simulation_results.csv")
