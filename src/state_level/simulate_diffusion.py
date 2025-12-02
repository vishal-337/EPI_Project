import os
import pandas as pd
import networkx as nx
import numpy as np
import random

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
DATA = os.path.join(PROJECT_ROOT, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(PROJECT_ROOT, "outputs")

EDGES_PATH = os.path.join(OUT, "influence_edges.csv")
PANEL_PATH = os.path.join(PROC, "dispensing_with_is_high.csv")

def main():
    print("--- LOADING DATA ---")
    if not os.path.exists(EDGES_PATH):
        print("Error: Edges file not found.")
        return
    
    edges_df = pd.read_csv(EDGES_PATH)
    panel_df = pd.read_csv(PANEL_PATH)
    
    G = nx.DiGraph()
    for _, row in edges_df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    
    years = sorted(panel_df["YEAR"].unique())
    
    results = []
    
    print("\n--- STARTING DIFFUSION REPLAY (One-Step-Ahead Prediction) ---")
    print("Task: Given the set of High states in year T, predict the NEW High states in year T+1.")
    
    total_correct = 0
    total_predicted = 0
    
    for i in range(len(years) - 1):
        t = years[i]
        next_t = years[i+1]
        
        current_high = set(panel_df[(panel_df["YEAR"] == t) & (panel_df["is_high"] == 1)]["STATE_ABBREV"])
        
        next_high = set(panel_df[(panel_df["YEAR"] == next_t) & (panel_df["is_high"] == 1)]["STATE_ABBREV"])
        
        actual_new = next_high - current_high
        
        if not actual_new:
            continue
            
        k = len(actual_new)
        
        candidates = []
        all_states = set(panel_df["STATE_ABBREV"].unique())
        potential_targets = all_states - current_high
        
        candidate_scores = []
        for state in potential_targets:
            net_score = 0
            if G.has_node(state):
                for source, _, data in G.in_edges(state, data=True):
                    if source in current_high:
                        net_score += data['weight']
            
            try:
                current_rate = panel_df[(panel_df["YEAR"] == t) & (panel_df["STATE_ABBREV"] == state)]["opioid_dispensing_rate"].values[0]
            except IndexError:
                current_rate = 0.0
                
            try:
                prev_rate = panel_df[(panel_df["YEAR"] == t-1) & (panel_df["STATE_ABBREV"] == state)]["opioid_dispensing_rate"].values[0]
            except IndexError:
                prev_rate = current_rate
            
            susceptibility = current_rate / 87.35
            
            if prev_rate > 0:
                momentum = (current_rate - prev_rate) / prev_rate
            else:
                momentum = 0.0
            
            epsilon = 0.05
            
            final_score = (net_score + epsilon) * (susceptibility ** 2) * (1.0 + max(0, momentum))
            
            candidate_scores.append((state, final_score))
        
        candidate_scores.sort(key=lambda x: x[1], reverse=True)
        
        predicted_new = set([x[0] for x in candidate_scores[:k]])
        
        correct_hits = predicted_new.intersection(actual_new)
        num_correct = len(correct_hits)
        
        precision = num_correct / k if k > 0 else 0
        
        if len(potential_targets) >= k:
            expected_random = (k * k) / len(potential_targets)
        else:
            expected_random = 0
            
        print(f"\nYear {t} -> {next_t}")
        print(f"  Actual New Adopters ({k}): {sorted(list(actual_new))}")
        print(f"  Predicted Top-{k}: {sorted(list(predicted_new))}")
        print(f"  Correct: {sorted(list(correct_hits))} (Count: {num_correct})")
        print(f"  Accuracy: {precision:.2%} (vs Random Exp: {expected_random:.2f})")
        
        results.append({
            "Year": next_t,
            "Actual_Count": k,
            "Correct_Count": num_correct,
            "Accuracy": precision,
            "Random_Exp": expected_random
        })
        
        total_correct += num_correct
        total_predicted += k

    # --- Summary ---
    print("\n" + "="*40)
    print("SIMULATION SUMMARY")
    print("="*40)
    if total_predicted > 0:
        overall_acc = total_correct / total_predicted
        print(f"Overall Accuracy: {overall_acc:.2%} ({total_correct}/{total_predicted} correct predictions)")
    else:
        print("No adoption events found to predict.")
        
    res_df = pd.DataFrame(results)
    res_path = os.path.join(OUT, "simulation_results.csv")
    res_df.to_csv(res_path, index=False)
    print(f"Detailed results saved to {res_path}")

if __name__ == "__main__":
    main()
