import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
OUT = os.path.join(PROJECT_ROOT, "outputs")

def main():
    edges_path = os.path.join(OUT, "county_influence_edges.csv")
    if not os.path.exists(edges_path):
        return

    df = pd.read_csv(edges_path)
    
    # Create Graph
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['source_fips'], row['target_fips'], weight=row['weight'])
        
    # 1. Out-Degree Centrality
    out_degree = {}
    for node in G.nodes():
        weight_sum = sum(data['weight'] for _, _, data in G.out_edges(node, data=True))
        out_degree[node] = weight_sum
        
    # 2. Eigenvector Centrality
    try:
        eigen = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
    except:
        eigen = nx.eigenvector_centrality(G, max_iter=1000) # Fallback
        
    # Prepare DataFrame
    # We need to map FIPS back to names and states
    # The edges df has this info, let's create a lookup
    fips_meta = df[["source_fips", "source_name", "STATE_ABBREV"]].drop_duplicates("source_fips").set_index("source_fips")
    # Also need target fips metadata if they are not in sources (unlikely for high influence but possible)
    target_meta = df[["target_fips", "target_name", "STATE_ABBREV"]].drop_duplicates("target_fips").set_index("target_fips")
    meta = fips_meta.combine_first(target_meta)
    
    results = []
    for node in G.nodes():
        if node in meta.index:
            name = meta.loc[node, "source_name"] if "source_name" in meta.columns else meta.loc[node, "target_name"]
            state = meta.loc[node, "STATE_ABBREV"]
            results.append({
                "FIPS": node,
                "COUNTY_NAME": name,
                "STATE_ABBREV": state,
                "influence_score": out_degree.get(node, 0),
                "eigenvector_centrality": eigen.get(node, 0)
            })
            
    ranking = pd.DataFrame(results)
    ranking = ranking.sort_values("influence_score", ascending=False)
    
    ranking.to_csv(os.path.join(OUT, "county_influence_rankings.csv"), index=False)
    
    # Plot Top 10 Overall
    top10 = ranking.head(10).sort_values("influence_score", ascending=True)
    
    plt.figure(figsize=(10, 6))
    labels = top10["COUNTY_NAME"] + ", " + top10["STATE_ABBREV"]
    plt.barh(labels, top10["influence_score"], color="#2ca02c")
    plt.xlabel("Influence Score (Weighted Out-Degree)")
    plt.title("Top 10 Most Influential Counties (Intra-State)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "top_influential_counties.png"))

if __name__ == "__main__":
    main()