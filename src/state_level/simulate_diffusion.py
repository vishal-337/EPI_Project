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
    
    # Build Graph
    G = nx.DiGraph()
    for _, row in edges_df.iterrows():
        G.add_edge(row['source'], row['target'], weight=row['weight'])
    
    print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    
    # Prepare Ground Truth
    # We need to know who is high in each year
    years = sorted(panel_df["YEAR"].unique())
    
    # Metrics storage
    results = []
    
    print("\n--- STARTING DIFFUSION REPLAY (One-Step-Ahead Prediction) ---")
    print("Task: Given the set of High states in year T, predict the NEW High states in year T+1.")
    
    total_correct = 0
    total_predicted = 0
    
    for i in range(len(years) - 1):
        t = years[i]
        next_t = years[i+1]
        
        # 1. Identify Current Active Set (Ground Truth at year t)
        current_high = set(panel_df[(panel_df["YEAR"] == t) & (panel_df["is_high"] == 1)]["STATE_ABBREV"])
        
        # 2. Identify Actual New Adopters in T+1
        next_high = set(panel_df[(panel_df["YEAR"] == next_t) & (panel_df["is_high"] == 1)]["STATE_ABBREV"])
        
        # New adopters are those high in T+1 but NOT high in T
        actual_new = next_high - current_high
        
        if not actual_new:
            # No diffusion event this year
            continue
            
        k = len(actual_new)
        
        # 3. Predict Risk for all Candidates
        # Candidates are states that are NOT currently high
        candidates = []
        all_states = set(panel_df["STATE_ABBREV"].unique())
        potential_targets = all_states - current_high
        
        candidate_scores = []
        for state in potential_targets:
            # A. Network Pressure: Sum of weights from currently high neighbors
            net_score = 0
            if G.has_node(state):
                for source, _, data in G.in_edges(state, data=True):
                    if source in current_high:
                        net_score += data['weight']
            
            # B. Susceptibility & Momentum
            try:
                current_rate = panel_df[(panel_df["YEAR"] == t) & (panel_df["STATE_ABBREV"] == state)]["opioid_dispensing_rate"].values[0]
            except IndexError:
                current_rate = 0.0
                
            try:
                prev_rate = panel_df[(panel_df["YEAR"] == t-1) & (panel_df["STATE_ABBREV"] == state)]["opioid_dispensing_rate"].values[0]
            except IndexError:
                prev_rate = current_rate
            
            # Susceptibility (normalized)
            susceptibility = current_rate / 87.35
            
            # Momentum (Growth rate)
            if prev_rate > 0:
                momentum = (current_rate - prev_rate) / prev_rate
            else:
                momentum = 0.0
            
            # C. Combined Score
            # Formula: (Network + epsilon) * Susceptibility^2 * (1 + Momentum)
            # Epsilon allows for spontaneous adoption (internal momentum) even without network pressure
            epsilon = 0.05
            
            final_score = (net_score + epsilon) * (susceptibility ** 2) * (1.0 + max(0, momentum))
            
            candidate_scores.append((state, final_score))
        
        # 4. Rank and Select Top K
        # Sort by score descending
        candidate_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Prediction: Top k states
        predicted_new = set([x[0] for x in candidate_scores[:k]])
        
        # 5. Evaluate
        correct_hits = predicted_new.intersection(actual_new)
        num_correct = len(correct_hits)
        
        precision = num_correct / k if k > 0 else 0
        # Recall is same as precision here because we predict exactly k items
        
        # Random Baseline for comparison
        random_correct = 0
        if len(potential_targets) >= k:
            # Expected value of random guessing = k * (k / N)
            # But let's just simulate one random draw or use expected value
            # Expected correct = k * (k / len(potential_targets))
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
        
    # Save results
    res_df = pd.DataFrame(results)
    res_path = os.path.join(OUT, "simulation_results.csv")
    res_df.to_csv(res_path, index=False)
    print(f"Detailed results saved to {res_path}")

if __name__ == "__main__":
    main()
