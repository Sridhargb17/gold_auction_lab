import pandas as pd
from data_group import analyze_weights
from rate_fetch import extract_lot_prices
from core_logic import apply_business_logic

def run_pipeline(file_path, gold_rate_18k, office_location="Vellore"):
    """
    Main execution function for the UI and API.
    """
    # 1. Extract Weights & Prices
    grouped_df = analyze_weights(file_path)
    rates_df = extract_lot_prices(file_path)

    if grouped_df.empty:
        return pd.DataFrame()

    # 2. Merge Data
    grouped_df.reset_index(inplace=True)
    # Ensure Lot No is string for clean merging
    grouped_df['Lot No'] = grouped_df['Lot No'].astype(str)
    rates_df['Lot No'] = rates_df['Lot No'].astype(str)
    
    final_df = pd.merge(grouped_df, rates_df, on='Lot No', how='outer')

    # 3. Apply Business Logic (18K Rate + 3% GST + Vellore Proximity)
    final_df = apply_business_logic(final_df, gold_rate_18k, office_location)

    return final_df

if __name__ == "__main__":
    # Standard CLI execution if needed
    path = r"C:\Users\Guest1\Workspace\gold_analysis\Samil_3-2-2026_12-33-48_PM_Inventory_List.xls"
    results = run_pipeline(path, 13100)
    print(results.head())