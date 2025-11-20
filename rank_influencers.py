import os
import pandas as pd
import networkx as nx

ROOT = os.path.abspath(os.path.dirname(__file__))
OUT = os.path.join(ROOT, "outputs")
edges_path = os.path.join(OUT, "influence_edges.csv")

df = pd.read_csv(edges_path)
G = nx.DiGraph()
for _, r in df.iterrows():
    G.add_edge(r["source"], r["target"], weight=r["weight"])

eigen = nx.eigenvector_centrality(G.reverse(), max_iter=1000, weight="weight")
degree = nx.out_degree_centrality(G)
between = nx.betweenness_centrality(G, weight="weight")

rankings = pd.DataFrame({
    "STATE_ABBREV": list(eigen.keys()),
    "eigenvector": list(eigen.values()),
    "out_degree": [degree[k] for k in eigen.keys()],
    "betweenness": [between[k] for k in eigen.keys()]
})

rankings = rankings.sort_values("eigenvector", ascending=False)
rankings.to_csv(os.path.join(OUT, "influencer_rankings.csv"), index=False)
print("Rankings saved to outputs/influencer_rankings.csv")
