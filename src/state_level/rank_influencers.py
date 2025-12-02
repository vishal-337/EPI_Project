import os
import pandas as pd
import networkx as nx
import numpy as np

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
OUT = os.path.join(PROJECT_ROOT, "outputs")
EDGES_PATH = os.path.join(OUT, "influence_edges.csv")

def main():
    if not os.path.exists(EDGES_PATH):
        print(f"Error: {EDGES_PATH} not found. Please run build_influence_network.py first.")
        return

    print(f"Loading edges from {EDGES_PATH}...")
    edges_df = pd.read_csv(EDGES_PATH)
    
    G = nx.DiGraph()
    
    for _, row in edges_df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
        
    print(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")

    out_degree_centrality = {}
    for node in G.nodes():
        weight_sum = sum(data['weight'] for _, _, data in G.out_edges(node, data=True))
        out_degree_centrality[node] = weight_sum

    try:
        eigen_centrality = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
    except nx.PowerIterationFailedConvergence:
        print("Warning: Eigenvector centrality did not converge. Using unweighted fallback or partial results.")
        eigen_centrality = nx.eigenvector_centrality(G, max_iter=1000)

    betweenness_centrality = nx.betweenness_centrality(G, weight='weight')

    nodes = list(G.nodes())
    rank_df = pd.DataFrame({
        'STATE_ABBREV': nodes,
        'Out_Degree_Weight': [out_degree_centrality.get(n, 0) for n in nodes],
        'Eigenvector': [eigen_centrality.get(n, 0) for n in nodes],
        'Betweenness': [betweenness_centrality.get(n, 0) for n in nodes]
    })

    rank_df = rank_df.sort_values('Out_Degree_Weight', ascending=False).reset_index(drop=True)
    
    rank_df['Rank_OutDegree'] = rank_df['Out_Degree_Weight'].rank(ascending=False, method='min')
    rank_df['Rank_Eigenvector'] = rank_df['Eigenvector'].rank(ascending=False, method='min')
    rank_df['Rank_Betweenness'] = rank_df['Betweenness'].rank(ascending=False, method='min')

    cols = ['STATE_ABBREV', 
            'Rank_OutDegree', 'Out_Degree_Weight', 
            'Rank_Eigenvector', 'Eigenvector', 
            'Rank_Betweenness', 'Betweenness']
    rank_df = rank_df[cols]

    out_path = os.path.join(OUT, "state_influence_rankings.csv")
    rank_df.to_csv(out_path, index=False)
    print(f"\nRankings saved to {out_path}")

    print("\n" + "="*50)
    print("CUMULATIVE INFLUENCE (2006-2018)")
    print("="*50)
    print("TOP 10 INFLUENTIAL STATES (By Out-Degree Weight)")
    print(rank_df.head(10).to_string(index=False))

    print("\n" + "="*50)
    print("TOP 5 BY EIGENVECTOR CENTRALITY (Connected to other influencers)")
    print("="*50)
    print(rank_df.sort_values('Eigenvector', ascending=False).head(5)[['STATE_ABBREV', 'Eigenvector', 'Rank_Eigenvector']].to_string(index=False))

    print("\n" + "="*50)
    print("TEMPORAL EVOLUTION OF INFLUENCE (Cumulative by Year)")
    print("="*50)

if __name__ == "__main__":
    main()
