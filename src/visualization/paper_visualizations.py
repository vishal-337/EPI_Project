"""
Enhanced Visualizations for State-Level Opioid Analysis Paper

Generates:
1. Network evolution over time (multi-panel)
2. Geographic cluster map
3. Rate trajectories for key states
4. Model performance analysis
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from matplotlib.lines import Line2D

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
DATA = os.path.join(PROJECT_ROOT, "data")
PROC = os.path.join(DATA, "processed")
OUT = os.path.join(PROJECT_ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

# Approximate US state positions for network layout (lon, lat scaled)
STATE_POSITIONS = {
    'WA': (0.12, 0.92), 'OR': (0.10, 0.78), 'CA': (0.08, 0.55), 'NV': (0.15, 0.60),
    'ID': (0.22, 0.78), 'MT': (0.30, 0.90), 'WY': (0.32, 0.72), 'UT': (0.23, 0.58),
    'AZ': (0.20, 0.40), 'CO': (0.35, 0.55), 'NM': (0.30, 0.38), 'ND': (0.45, 0.90),
    'SD': (0.45, 0.78), 'NE': (0.45, 0.65), 'KS': (0.47, 0.52), 'OK': (0.48, 0.42),
    'TX': (0.45, 0.28), 'MN': (0.55, 0.82), 'IA': (0.55, 0.65), 'MO': (0.58, 0.52),
    'AR': (0.58, 0.42), 'LA': (0.58, 0.28), 'WI': (0.62, 0.78), 'IL': (0.62, 0.62),
    'MI': (0.72, 0.75), 'IN': (0.70, 0.58), 'OH': (0.78, 0.58), 'KY': (0.75, 0.48),
    'TN': (0.72, 0.42), 'MS': (0.62, 0.35), 'AL': (0.68, 0.35), 'GA': (0.78, 0.35),
    'FL': (0.82, 0.20), 'SC': (0.82, 0.38), 'NC': (0.85, 0.45), 'VA': (0.85, 0.52),
    'WV': (0.80, 0.52), 'PA': (0.85, 0.62), 'NY': (0.88, 0.72), 'NJ': (0.92, 0.60),
    'DE': (0.92, 0.55), 'MD': (0.88, 0.52), 'CT': (0.95, 0.68), 'RI': (0.97, 0.68),
    'MA': (0.97, 0.72), 'VT': (0.92, 0.82), 'NH': (0.95, 0.80), 'ME': (0.98, 0.88),
    'AK': (0.15, 0.15), 'HI': (0.25, 0.15), 'DC': (0.90, 0.50)
}

NEIGHBORS = {
    'AL': ['FL', 'GA', 'MS', 'TN'], 'AK': [], 'AZ': ['CA', 'CO', 'NV', 'NM', 'UT'],
    'AR': ['LA', 'MS', 'MO', 'OK', 'TN', 'TX'], 'CA': ['AZ', 'NV', 'OR'],
    'CO': ['AZ', 'KS', 'NE', 'NM', 'OK', 'UT', 'WY'], 'CT': ['MA', 'NY', 'RI'],
    'DE': ['MD', 'NJ', 'PA'], 'FL': ['AL', 'GA'], 'GA': ['AL', 'FL', 'NC', 'SC', 'TN'],
    'HI': [], 'ID': ['MT', 'NV', 'OR', 'UT', 'WA', 'WY'], 'IL': ['IN', 'IA', 'KY', 'MO', 'WI'],
    'IN': ['IL', 'KY', 'MI', 'OH'], 'IA': ['IL', 'MN', 'MO', 'NE', 'SD', 'WI'],
    'KS': ['CO', 'MO', 'NE', 'OK'], 'KY': ['IL', 'IN', 'MO', 'OH', 'TN', 'VA', 'WV'],
    'LA': ['AR', 'MS', 'TX'], 'ME': ['NH'], 'MD': ['DE', 'PA', 'VA', 'WV'],
    'MA': ['CT', 'NH', 'NY', 'RI', 'VT'], 'MI': ['IN', 'OH', 'WI'],
    'MN': ['IA', 'ND', 'SD', 'WI'], 'MS': ['AL', 'AR', 'LA', 'TN'],
    'MO': ['AR', 'IL', 'IA', 'KS', 'KY', 'NE', 'OK', 'TN'], 'MT': ['ID', 'ND', 'SD', 'WY'],
    'NE': ['CO', 'IA', 'KS', 'MO', 'SD', 'WY'], 'NV': ['AZ', 'CA', 'ID', 'OR', 'UT'],
    'NH': ['ME', 'MA', 'VT'], 'NJ': ['DE', 'NY', 'PA'], 'NM': ['AZ', 'CO', 'OK', 'TX', 'UT'],
    'NY': ['CT', 'MA', 'NJ', 'PA', 'VT'], 'NC': ['GA', 'SC', 'TN', 'VA'],
    'ND': ['MN', 'MT', 'SD'], 'OH': ['IN', 'KY', 'MI', 'PA', 'WV'],
    'OK': ['AR', 'CO', 'KS', 'MO', 'NM', 'TX'], 'OR': ['CA', 'ID', 'NV', 'WA'],
    'PA': ['DE', 'MD', 'NJ', 'NY', 'OH', 'WV'], 'RI': ['CT', 'MA'], 'SC': ['GA', 'NC'],
    'SD': ['IA', 'MN', 'MT', 'NE', 'ND', 'WY'], 'TN': ['AL', 'AR', 'GA', 'KY', 'MS', 'MO', 'NC', 'VA'],
    'TX': ['AR', 'LA', 'NM', 'OK'], 'UT': ['AZ', 'CO', 'ID', 'NV', 'NM', 'WY'],
    'VT': ['MA', 'NH', 'NY'], 'VA': ['KY', 'MD', 'NC', 'TN', 'WV'], 'WA': ['ID', 'OR'],
    'WV': ['KY', 'MD', 'OH', 'PA', 'VA'], 'WI': ['IL', 'IA', 'MI', 'MN'],
    'WY': ['CO', 'ID', 'MT', 'NE', 'SD', 'UT'], 'DC': ['MD', 'VA']
}


def plot_network_evolution():
    """Create multi-panel showing network growth over key years."""
    print("Generating Network Evolution Plot...")
    
    panel_df = pd.read_csv(os.path.join(PROC, "dispensing_with_is_high.csv"))
    edges_df = pd.read_csv(os.path.join(OUT, "influence_edges.csv"))
    adoption_df = pd.read_csv(os.path.join(PROC, "adoption_year.csv"))
    
    adoption_map = dict(zip(adoption_df["STATE_ABBREV"], adoption_df["adoption_year"]))
    
    years = [2006, 2008, 2010, 2012]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    axes = axes.flatten()
    
    for idx, year in enumerate(years):
        ax = axes[idx]
        
        high_states = set(panel_df[(panel_df["YEAR"] <= year) & (panel_df["is_high"] == 1)]["STATE_ABBREV"].unique())
        
        active_edges = []
        for _, row in edges_df.iterrows():
            target_adopt = adoption_map.get(row['target'], 9999)
            if target_adopt <= year:
                active_edges.append((row['source'], row['target'], row['weight']))
        
        G = nx.DiGraph()
        for s, t, w in active_edges:
            G.add_edge(s, t, weight=w)
        
        all_states = set(panel_df["STATE_ABBREV"].unique())
        for state in all_states:
            if state not in G:
                G.add_node(state)
        
        pos = {s: STATE_POSITIONS.get(s, (0.5, 0.5)) for s in G.nodes()}
        node_colors = ['#e74c3c' if s in high_states else '#3498db' for s in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=300, node_color=node_colors, alpha=0.8)
        
        if active_edges:
            edge_weights = [G[u][v]['weight'] * 2 for u, v in G.edges()]
            nx.draw_networkx_edges(G, pos, ax=ax, width=edge_weights, alpha=0.6, 
                                   edge_color='#2c3e50', arrows=True, arrowsize=15,
                                   connectionstyle="arc3,rad=0.1")
        
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=7, font_weight='bold')
        
        ax.set_title(f"Year {year}\n{len(high_states)} High-Prescribing States, {len(active_edges)} Influence Events", 
                     fontsize=12, fontweight='bold')
        ax.axis('off')
    
    legend_elements = [
        mpatches.Patch(color='#e74c3c', label='High-Prescribing State'),
        mpatches.Patch(color='#3498db', label='Low-Prescribing State'),
        Line2D([0], [0], color='#2c3e50', linewidth=2, label='Influence Edge')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=11, 
               bbox_to_anchor=(0.5, 0.02))
    
    plt.suptitle("Evolution of Opioid Prescribing Influence Network (2006-2012)", 
                 fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(os.path.join(OUT, "network_evolution.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: network_evolution.png")


def plot_rate_trajectories():
    """Show rate trajectories for key states over time."""
    print("Generating Rate Trajectories Plot...")
    
    df = pd.read_csv(os.path.join(PROC, "dispensing_state_year.csv"))
    rankings = pd.read_csv(os.path.join(OUT, "state_influence_rankings.csv"))
    
    top_states = rankings.head(5)["STATE_ABBREV"].tolist()
    low_states = ['CA', 'NY', 'MN']
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    for state in top_states:
        state_data = df[df["STATE_ABBREV"] == state].sort_values("YEAR")
        ax.plot(state_data["YEAR"], state_data["opioid_dispensing_rate"], 
                marker='o', linewidth=2.5, markersize=5, label=f"{state} (Influencer)")
    
    for state in low_states:
        state_data = df[df["STATE_ABBREV"] == state].sort_values("YEAR")
        ax.plot(state_data["YEAR"], state_data["opioid_dispensing_rate"], 
                linestyle='--', linewidth=1.5, alpha=0.7, label=f"{state} (Low)")
    
    ax.axhline(y=87.35, color='red', linestyle=':', linewidth=2, label='High Threshold (87.35)')
    
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Opioid Dispensing Rate (per 100 persons)", fontsize=12)
    ax.set_title("Prescribing Rate Trajectories: Top Influencers vs Low-Prescribing States", 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "rate_trajectories.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: rate_trajectories.png")


def plot_geographic_map():
    """Create a simplified geographic visualization showing clusters."""
    print("Generating Geographic Cluster Map...")
    
    adoption_df = pd.read_csv(os.path.join(PROC, "adoption_year.csv"))
    adoption_map = dict(zip(adoption_df["STATE_ABBREV"], adoption_df["adoption_year"]))
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    all_states = list(STATE_POSITIONS.keys())
    cmap = plt.cm.YlOrRd
    min_year, max_year = 2006, 2012
    
    for state in all_states:
        x, y = STATE_POSITIONS[state]
        
        if state in adoption_map:
            year = adoption_map[state]
            color = cmap((year - min_year) / (max_year - min_year + 1))
            ax.scatter(x, y, s=800, c=[color], edgecolors='black', linewidths=1.5, zorder=3)
            ax.text(x, y, state, ha='center', va='center', fontsize=8, fontweight='bold', color='white', zorder=4)
        else:
            ax.scatter(x, y, s=600, c='lightgray', edgecolors='black', linewidths=1, zorder=2, alpha=0.7)
            ax.text(x, y, state, ha='center', va='center', fontsize=7, color='gray', zorder=4)
    
    for state, neighbors in NEIGHBORS.items():
        if state in STATE_POSITIONS:
            x1, y1 = STATE_POSITIONS[state]
            for neighbor in neighbors:
                if neighbor in STATE_POSITIONS:
                    x2, y2 = STATE_POSITIONS[neighbor]
                    ax.plot([x1, x2], [y1, y2], 'k-', alpha=0.1, linewidth=0.5, zorder=1)
    
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=min_year, vmax=max_year))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.6, pad=0.02)
    cbar.set_label('Year of High-Prescribing Adoption', fontsize=11)
    
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(0.05, 1.0)
    ax.set_title("Geographic Distribution of High-Prescribing Adoption\n(Gray = Never Exceeded Threshold)", 
                 fontsize=14, fontweight='bold')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "geographic_clusters.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: geographic_clusters.png")


def plot_model_performance():
    """Detailed model performance visualization."""
    print("Generating Model Performance Plot...")
    
    results_df = pd.read_csv(os.path.join(OUT, "continuous_prediction_results.csv"))
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. Scatter plot with error bands
    ax1 = axes[0, 0]
    ax1.scatter(results_df["Actual_Rate"], results_df["Predicted_Rate"], alpha=0.5, c='#3498db', s=30)
    
    min_val = min(results_df["Actual_Rate"].min(), results_df["Predicted_Rate"].min())
    max_val = max(results_df["Actual_Rate"].max(), results_df["Predicted_Rate"].max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'r-', linewidth=2, label='Perfect Prediction')
    ax1.fill_between([min_val, max_val], [min_val-10, max_val-10], [min_val+10, max_val+10], 
                     alpha=0.2, color='green', label='±10 Error Band')
    
    ax1.set_xlabel("Actual Rate", fontsize=11)
    ax1.set_ylabel("Predicted Rate", fontsize=11)
    ax1.set_title("Actual vs Predicted (R² = 0.884)", fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Error distribution
    ax2 = axes[0, 1]
    errors = results_df["Error"]
    ax2.hist(errors, bins=30, color='#e74c3c', edgecolor='white', alpha=0.7)
    ax2.axvline(x=0, color='black', linestyle='--', linewidth=2)
    ax2.axvline(x=errors.mean(), color='blue', linestyle='-', linewidth=2, label=f'Mean Error: {errors.mean():.2f}')
    ax2.set_xlabel("Prediction Error (Actual - Predicted)", fontsize=11)
    ax2.set_ylabel("Frequency", fontsize=11)
    ax2.set_title("Error Distribution", fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Error by year
    ax3 = axes[1, 0]
    year_errors = results_df.groupby("YEAR")["Error"].agg(['mean', 'std']).reset_index()
    ax3.bar(year_errors["YEAR"], year_errors["mean"], yerr=year_errors["std"], 
            color='#9b59b6', capsize=5, alpha=0.8)
    ax3.axhline(y=0, color='black', linestyle='--')
    ax3.set_xlabel("Year", fontsize=11)
    ax3.set_ylabel("Mean Prediction Error", fontsize=11)
    ax3.set_title("Prediction Error by Year", fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Top/Bottom predicted states
    ax4 = axes[1, 1]
    state_errors = results_df.groupby("STATE_ABBREV")["Error"].mean().sort_values()
    
    worst_under = state_errors.head(5)
    worst_over = state_errors.tail(5)
    combined = pd.concat([worst_under, worst_over])
    
    colors = ['#e74c3c' if v < 0 else '#27ae60' for v in combined.values]
    ax4.barh(range(len(combined)), combined.values, color=colors)
    ax4.set_yticks(range(len(combined)))
    ax4.set_yticklabels(combined.index)
    ax4.axvline(x=0, color='black', linestyle='-')
    ax4.set_xlabel("Mean Prediction Error", fontsize=11)
    ax4.set_title("States with Largest Prediction Errors\n(Red = Over-predicted, Green = Under-predicted)", 
                  fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='x')
    
    plt.suptitle("Spatial Autoregressive Model Performance Analysis", fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "model_performance_detailed.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("  Saved: model_performance_detailed.png")


def main():
    print("="*60)
    print("GENERATING VISUALIZATIONS FOR PAPER")
    print("="*60)
    
    plot_network_evolution()
    plot_rate_trajectories()
    plot_geographic_map()
    plot_model_performance()
    
    print("\n" + "="*60)
    print("ALL VISUALIZATIONS COMPLETE!")
    print("="*60)
    print("\nGenerated files in outputs/:")
    print("  1. network_evolution.png          - Network growth over 4 key years")
    print("  2. rate_trajectories.png          - Rate trends for key states")
    print("  3. geographic_clusters.png        - Map showing adoption timing")
    print("  4. model_performance_detailed.png - Prediction model analysis")


if __name__ == "__main__":
    main()
