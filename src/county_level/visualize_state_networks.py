"""
Generate per-state county influence network visualizations and top 10 rankings.

Outputs:
- outputs/state_networks/  - Network graph PNG for each state
- outputs/county_top10_by_state.csv - Top 10 influential counties per state
"""

import os
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
OUT = os.path.join(PROJECT_ROOT, "outputs")
NETWORKS_DIR = os.path.join(OUT, "state_networks")
os.makedirs(NETWORKS_DIR, exist_ok=True)


def plot_state_network(state, edges_df, rankings_df):
    """Create network visualization for a single state."""
    
    state_edges = edges_df[edges_df["STATE_ABBREV"] == state]
    state_ranks = rankings_df[rankings_df["STATE_ABBREV"] == state]
    
    if state_edges.empty:
        return None
    
    # Build graph
    G = nx.DiGraph()
    for _, row in state_edges.iterrows():
        G.add_edge(row["source_fips"], row["target_fips"], weight=row["weight"])
    
    # Get node metadata
    fips_to_name = {}
    for _, row in state_edges.iterrows():
        fips_to_name[row["source_fips"]] = row["source_name"]
        fips_to_name[row["target_fips"]] = row["target_name"]
    
    # Calculate node sizes based on influence score
    influence_map = dict(zip(state_ranks["FIPS"], state_ranks["influence_score"]))
    max_influence = state_ranks["influence_score"].max() if not state_ranks.empty else 1
    
    node_sizes = []
    node_colors = []
    for node in G.nodes():
        inf_score = influence_map.get(node, 0)
        # Scale node size: min 100, max 1500
        size = 100 + (inf_score / max_influence) * 1400 if max_influence > 0 else 200
        node_sizes.append(size)
        # Color: more influential = darker red
        node_colors.append(inf_score / max_influence if max_influence > 0 else 0.5)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Layout
    if len(G.nodes()) > 50:
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    else:
        pos = nx.spring_layout(G, k=3, iterations=100, seed=42)
    
    # Draw edges
    edge_weights = [G[u][v]["weight"] for u, v in G.edges()]
    max_weight = max(edge_weights) if edge_weights else 1
    edge_widths = [0.5 + (w / max_weight) * 2 for w in edge_weights]
    
    nx.draw_networkx_edges(G, pos, ax=ax, width=edge_widths, alpha=0.4,
                           edge_color='#666666', arrows=True, arrowsize=10,
                           connectionstyle="arc3,rad=0.1")
    
    # Draw nodes
    nodes = nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes,
                                   node_color=node_colors, cmap=plt.cm.YlOrRd,
                                   alpha=0.8, edgecolors='black', linewidths=0.5)
    
    # Labels for top nodes only (top 10 by influence)
    top_nodes = state_ranks.head(10)["FIPS"].tolist()
    labels = {node: fips_to_name.get(node, str(node))[:15] for node in G.nodes() if node in top_nodes}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=7, font_weight='bold')
    
    # Title and stats
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    top_county = state_ranks.iloc[0]["COUNTY_NAME"] if not state_ranks.empty else "N/A"
    
    ax.set_title(f"{state} County Influence Network\n{n_nodes} Counties, {n_edges} Influence Edges\nTop Influencer: {top_county}",
                 fontsize=14, fontweight='bold')
    ax.axis('off')
    
    # Colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=plt.Normalize(0, max_influence))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label('Influence Score', fontsize=10)
    
    plt.tight_layout()
    return fig


def main():
    print("=" * 60)
    print("GENERATING STATE-LEVEL COUNTY NETWORK VISUALIZATIONS")
    print("=" * 60)
    
    # Load data
    edges_path = os.path.join(OUT, "county_influence_edges.csv")
    ranks_path = os.path.join(OUT, "county_influence_rankings.csv")
    
    if not os.path.exists(edges_path) or not os.path.exists(ranks_path):
        print("ERROR: Missing required files. Run build_intra_state_networks.py and rank_county_influencers.py first.")
        return
    
    edges_df = pd.read_csv(edges_path)
    rankings_df = pd.read_csv(ranks_path)
    
    states = sorted(edges_df["STATE_ABBREV"].unique())
    print(f"\nProcessing {len(states)} states...\n")
    
    # Generate top 10 per state
    top10_all = []
    
    for state in states:
        state_ranks = rankings_df[rankings_df["STATE_ABBREV"] == state].head(10).copy()
        state_ranks["rank_in_state"] = range(1, len(state_ranks) + 1)
        top10_all.append(state_ranks)
        
        # Generate network plot
        fig = plot_state_network(state, edges_df, rankings_df)
        if fig:
            fig_path = os.path.join(NETWORKS_DIR, f"{state}_network.png")
            fig.savefig(fig_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            
            n_counties = len(rankings_df[rankings_df["STATE_ABBREV"] == state])
            print(f"  {state}: Saved network ({n_counties} counties)")
    
    # Save consolidated top 10 CSV
    top10_df = pd.concat(top10_all, ignore_index=True)
    top10_df = top10_df[["STATE_ABBREV", "rank_in_state", "FIPS", "COUNTY_NAME", "influence_score", "eigenvector_centrality"]]
    top10_path = os.path.join(OUT, "county_top10_by_state.csv")
    top10_df.to_csv(top10_path, index=False)
    
    print(f"\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - {len(states)} network graphs in: outputs/state_networks/")
    print(f"  - Top 10 rankings: {top10_path}")
    
    # Print summary table
    print(f"\n{'='*60}")
    print("TOP INFLUENCER BY STATE")
    print(f"{'='*60}")
    print(f"{'State':<8} {'Top County':<30} {'Score':>10}")
    print("-" * 50)
    
    for state in states:
        state_ranks = rankings_df[rankings_df["STATE_ABBREV"] == state]
        if not state_ranks.empty:
            top = state_ranks.iloc[0]
            print(f"{state:<8} {top['COUNTY_NAME'][:28]:<30} {top['influence_score']:>10.2f}")


if __name__ == "__main__":
    main()
