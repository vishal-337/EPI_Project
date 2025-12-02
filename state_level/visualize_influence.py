import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
OUT = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

edges_path = os.path.join(OUT, "influence_edges.csv")
df = pd.read_csv(edges_path)

G = nx.DiGraph()
for _, r in df.iterrows():
    s = str(r["source"]) 
    t = str(r["target"]) 
    w = float(r["weight"]) 
    if G.has_edge(s, t):
        G[s][t]["weight"] += w
    else:
        G.add_edge(s, t, weight=w)

out_strength = {n: sum(d.get("weight", 1.0) for _, _, d in G.out_edges(n, data=True)) for n in G.nodes()}
sizes = [max(200, 50 * out_strength.get(n, 0.0)) for n in G.nodes()]
weights = [max(0.5, 0.8 * d.get("weight", 1.0)) for _, _, d in G.edges(data=True)]

pos = nx.spring_layout(G, seed=42, k=0.8)
plt.figure(figsize=(12, 9), dpi=150)
nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color="#4f46e5", alpha=0.85)
nx.draw_networkx_edges(G, pos, width=weights, edge_color="#111827", alpha=0.4, arrows=True, arrowsize=10)
nx.draw_networkx_labels(G, pos, font_size=8, font_color="#111827")
plt.axis("off")
plt.tight_layout()
plt.savefig(os.path.join(OUT, "influence_network.png"))
plt.close()


