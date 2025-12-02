import os
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
OUT = os.path.join(PROJECT_ROOT, "outputs")
PROC = os.path.join(PROJECT_ROOT, "data", "processed")

def plot_network():
    print("Generating Network Graph...")
    edges_path = os.path.join(OUT, "influence_edges.csv")
    if not os.path.exists(edges_path):
        print("Skipping network graph: edges file not found.")
        return

    df = pd.read_csv(edges_path)
    G = nx.DiGraph()
    for _, r in df.iterrows():
        G.add_edge(r["source"], r["target"], weight=r["weight"])

    plt.figure(figsize=(12, 10))
    
    d = dict(G.degree(weight='weight'))
    node_sizes = [v * 100 + 300 for v in d.values()]
    
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='skyblue', alpha=0.9)
    nx.draw_networkx_edges(G, pos, width=[d['weight'] for u, v, d in G.edges(data=True)], 
                           edge_color='gray', alpha=0.6, arrowsize=20)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    plt.title("Opioid Influence Network (Geographically Constrained)", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "influence_network_graph.png"), dpi=300)
    plt.close()

def plot_rankings():
    print("Generating Rankings Chart...")
    rank_path = os.path.join(OUT, "state_influence_rankings.csv")
    if not os.path.exists(rank_path):
        print("Skipping rankings chart: file not found.")
        return

    df = pd.read_csv(rank_path).head(10).sort_values("Out_Degree_Weight", ascending=True)
    
    plt.figure(figsize=(10, 6))
    plt.barh(df["STATE_ABBREV"], df["Out_Degree_Weight"], color='#4c72b0')
    plt.xlabel("Cumulative Out-Degree Weight (Influence Score)")
    plt.title("Top 10 Most Influential States (2006-2018)")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "top_influencers_bar.png"), dpi=300)
    plt.close()

def plot_adoption_timeline():
    print("Generating Adoption Timeline...")
    adopt_path = os.path.join(PROC, "adoption_year.csv")
    if not os.path.exists(adopt_path):
        print("Skipping adoption timeline: file not found.")
        return

    df = pd.read_csv(adopt_path).sort_values("adoption_year")
    
    counts = df.groupby("adoption_year").size()
    cumulative = counts.cumsum()
    
    plt.figure(figsize=(10, 6))
    plt.fill_between(cumulative.index, cumulative.values, color='skyblue', alpha=0.4)
    plt.plot(cumulative.index, cumulative.values, color='blue', marker='o')
    
    plt.xlabel("Year")
    plt.ylabel("Cumulative Number of High-Prescribing States")
    plt.title("Historical Adoption of High Opioid Prescribing Rates")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "historical_adoption_curve.png"), dpi=300)
    plt.close()

if __name__ == "__main__":
    plot_network()
    plot_rankings()
    plot_adoption_timeline()
    print("All visualizations generated in 'outputs/' folder.")
