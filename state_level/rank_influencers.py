import os
import pandas as pd
import networkx as nx
import numpy as np

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
OUT = os.path.join(PROJECT_ROOT, "outputs")
EDGES_PATH = os.path.join(OUT, "influence_edges.csv")

def main():
    if not os.path.exists(EDGES_PATH):
        print(f"Error: {EDGES_PATH} not found. Please run build_influence_network.py first.")
        return

    print(f"Loading edges from {EDGES_PATH}...")
    edges_df = pd.read_csv(EDGES_PATH)
    
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add edges with weights
    for _, row in edges_df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
        
    print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

    # --- Compute Centrality Metrics ---
    
    # 1. Weighted Out-Degree Centrality (Total outgoing influence)
    # We calculate this manually as sum of weights of outgoing edges
    out_degree_centrality = {}
    for node in G.nodes():
        weight_sum = sum(data['weight'] for _, _, data in G.out_edges(node, data=True))
        out_degree_centrality[node] = weight_sum

    # 2. Eigenvector Centrality (Influence of neighbors)
    # Note: max_iter increased for convergence
    try:
        eigen_centrality = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        print("Warning: Eigenvector centrality did not converge. Using unweighted fallback or partial results.")
        eigen_centrality = nx.eigenvector_centrality(G, max_iter=1000)

    # 3. Betweenness Centrality (Bridge nodes)
    betweenness_centrality = nx.betweenness_centrality(G, weight='weight')

    # --- Combine and Rank ---
    
    # Create a DataFrame for rankings
    nodes = list(G.nodes())
    rank_df = pd.DataFrame({
        'STATE_ABBREV': nodes,
        'Out_Degree_Weight': [out_degree_centrality.get(n, 0) for n in nodes],
        'Eigenvector': [eigen_centrality.get(n, 0) for n in nodes],
        'Betweenness': [betweenness_centrality.get(n, 0) for n in nodes]
    })

    # Sort by Out-Degree primarily, but we can look at others too
    rank_df = rank_df.sort_values('Out_Degree_Weight', ascending=False).reset_index(drop=True)
    
    # Add rank columns
    rank_df['Rank_OutDegree'] = rank_df['Out_Degree_Weight'].rank(ascending=False, method='min')
    rank_df['Rank_Eigenvector'] = rank_df['Eigenvector'].rank(ascending=False, method='min')
    rank_df['Rank_Betweenness'] = rank_df['Betweenness'].rank(ascending=False, method='min')

    # Reorder columns
    cols = ['STATE_ABBREV', 
            'Rank_OutDegree', 'Out_Degree_Weight', 
            'Rank_Eigenvector', 'Eigenvector', 
            'Rank_Betweenness', 'Betweenness']
    rank_df = rank_df[cols]

    # Save to CSV
    out_path = os.path.join(OUT, "state_influence_rankings.csv")
    rank_df.to_csv(out_path, index=False)
    print(f"\nRankings saved to {out_path}")

    # --- Display Top Results ---
    print("\n" + "="*50)
    print("CUMULATIVE INFLUENCE (2006-2018)")
    print("="*50)
    print("TOP 10 INFLUENTIAL STATES (By Out-Degree Weight)")
    print(rank_df.head(10).to_string(index=False))

    print("\n" + "="*50)
    print("TOP 5 BY EIGENVECTOR CENTRALITY (Connected to other influencers)")
    print("="*50)
    print(rank_df.sort_values('Eigenvector', ascending=False).head(5)[['STATE_ABBREV', 'Eigenvector', 'Rank_Eigenvector']].to_string(index=False))

    # --- Temporal Evolution Analysis ---
    # We need to reconstruct the graph year by year to see how rankings evolve
    print("\n" + "="*50)
    print("TEMPORAL EVOLUTION OF INFLUENCE (Cumulative by Year)")
    print("="*50)
    
    # Load the raw panel data to know which years exist
    # We can't easily reconstruct the exact year-by-year edges from the aggregated CSV
    # So we will rely on the fact that the aggregated CSV is the sum.
    # Ideally, build_influence_network.py should output a year column.
    # For now, we will skip the detailed year-by-year re-computation in this script
    # and focus on the interpretation of the cumulative result.
    
    #print("Note: These rankings represent the accumulated influence over the entire study period.")
    #print("Early adopters (e.g., TN, SC) naturally have higher cumulative scores.")
    #print("States like FL (Rank #1 Eigenvector) show high connectivity to these early hubs.")

if __name__ == "__main__":
    main()
