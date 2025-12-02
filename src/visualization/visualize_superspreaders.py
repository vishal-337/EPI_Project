import os
import pandas as pd
import matplotlib.pyplot as plt

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
OUT = os.path.join(PROJECT_ROOT, "outputs")

def main():
    csv_path = os.path.join(OUT, "county_superspreaders.csv")
    if not os.path.exists(csv_path):
        print("Superspreaders file not found.")
        return

    df = pd.read_csv(csv_path)
    
    top_per_state = df.groupby("STATE_ABBREV").first().reset_index()
    
    top = top_per_state.nlargest(10, "years_early").sort_values("years_early", ascending=True)
    
    plt.figure(figsize=(10, 8))
    labels = top["COUNTY_NAME"] + ", " + top["STATE_ABBREV"]
    
    plt.barh(labels, top["years_early"], color="#d62728")
    plt.xlabel("Years Early (County Adoption - State Adoption)")
    plt.title("Top 'Super-Spreader' County by State\n(Adopted High Rates Before Their State)")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    out_file = os.path.join(OUT, "top_superspreaders.png")
    plt.savefig(out_file, dpi=300)
    print(f"Saved visualization to {out_file}")

if __name__ == "__main__":
    main()