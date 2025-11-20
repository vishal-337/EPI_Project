import os
import pandas as pd
import networkx as nx
import numpy as np

ROOT = os.path.abspath(os.path.dirname(__file__))
DATA = os.path.join(ROOT, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(ROOT, "outputs")

EDGES_PATH = os.path.join(OUT, "influence_edges.csv")
PANEL_PATH = os.path.join(PROC, "dispensing_with_is_high.csv")

def run_simulation(edges_df, panel_df, intervention_nodes=None, intervention_year=None, threshold=0.8):
    # Build Graph
    G = nx.DiGraph()
    for _, row in edges_df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
        
    years = sorted(panel_df["YEAR"].unique())
    
    # Initialize with actual 2006 data
    sim_high = set(panel_df[(panel_df["YEAR"] == 2006) & (panel_df["is_high"] == 1)]["STATE_ABBREV"])
    
    history = {2006: len(sim_high)}
    
    # Ensure intervention_nodes is a list/set
    if intervention_nodes and isinstance(intervention_nodes, str):
        intervention_nodes = [intervention_nodes]
    
    for t in range(2006, 2018): 
        next_t = t + 1
        all_states = set(panel_df["STATE_ABBREV"].unique())
        potential_targets = all_states - sim_high
        new_adopters = []
        
        for state in potential_targets:
            # A. Network Pressure
            net_score = 0
            if G.has_node(state):
                for source, _, data in G.in_edges(state, data=True):
                    # INTERVENTION CHECK:
                    # Check if source is in the blocked list
                    if intervention_nodes and source in intervention_nodes and t >= intervention_year:
                        continue
                        
                    if source in sim_high:
                        net_score += data['weight']
            
            # B. Susceptibility
            try:
                current_rate = panel_df[(panel_df["YEAR"] == t) & (panel_df["STATE_ABBREV"] == state)]["opioid_dispensing_rate"].values[0]
            except IndexError:
                current_rate = 0.0
            
            susceptibility = current_rate / 87.35
            
            # C. Score
            epsilon = 0.05
            final_score = (net_score + epsilon) * (susceptibility ** 2)
            
            if final_score > threshold:
                new_adopters.append(state)
        
        sim_high.update(new_adopters)
        history[next_t] = len(sim_high)
        
    return history

def main():
    print("--- LOADING DATA ---")
    if not os.path.exists(EDGES_PATH):
        print("Error: Edges file not found.")
        return
    
    edges_df = pd.read_csv(EDGES_PATH)
    panel_df = pd.read_csv(PANEL_PATH)
    
    sim_threshold = 0.8
    
    print(f"\n--- RUNNING BASELINE SIMULATION (Threshold={sim_threshold}) ---")
    baseline_hist = run_simulation(edges_df, panel_df, threshold=sim_threshold)
    print(baseline_hist)
    
    print("\n--- RUNNING INTERVENTION: Block Single Source (TN) ---")
    tn_hist = run_simulation(edges_df, panel_df, intervention_nodes=["TN"], intervention_year=2006, threshold=sim_threshold)
    print(tn_hist)
    
    print("\n--- RUNNING INTERVENTION: Block Regional Cluster (TN, SC, AL) ---")
    # Hypothesis: Blocking the entire "Southern Core" is necessary to stop spread
    region_hist = run_simulation(edges_df, panel_df, intervention_nodes=["TN", "SC", "AL"], intervention_year=2006, threshold=sim_threshold)
    print(region_hist)
    
    # Compare
    print("\n" + "="*60)
    print("INTERVENTION IMPACT ANALYSIS (Total High States in 2015)")
    print("="*60)
    base_2015 = baseline_hist.get(2015, 0)
    tn_2015 = tn_hist.get(2015, 0)
    reg_2015 = region_hist.get(2015, 0)
    
    print(f"Baseline: {base_2015} states")
    print(f"Block TN Only: {tn_2015} states (Reduction: {base_2015 - tn_2015})")
    print(f"Block Region (TN+SC+AL): {reg_2015} states (Reduction: {base_2015 - reg_2015})")
    
    if base_2015 > reg_2015:
        print("\nSUCCESS: Regional intervention significantly reduced the spread!")
    else:
        print("\nRESULT: Still no change. The contagion is extremely robust.")

    # Save Intervention Results for Plotting
    years = sorted(baseline_hist.keys())
    results_data = []
    for y in years:
        results_data.append({
            "Year": y,
            "Baseline": baseline_hist.get(y, 0),
            "Block_TN": tn_hist.get(y, 0),
            "Block_Region": region_hist.get(y, 0)
        })
    
    intervention_df = pd.DataFrame(results_data)
    intervention_path = os.path.join(OUT, "intervention_results.csv")
    intervention_df.to_csv(intervention_path, index=False)
    print(f"\nIntervention results saved to {intervention_path}")

if __name__ == "__main__":
    main()
