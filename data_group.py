import pandas as pd

def analyze_weights(file_path):
    """Groups inventory by Lot No and calculates net and gross weight totals."""
    try:
        # Load the data, assuming the first row is the header
        df = pd.read_excel(file_path, header=0, sheet_name=0)
    except Exception as e:
        print(f"--- ERROR: Could not read the main inventory sheet: {e} ---")
        return pd.DataFrame() # Return empty DataFrame on failure

    # Clean headers immediately to prevent KeyErrors
    df.columns = df.columns.astype(str).str.strip()

    # Define target columns
    lot_col = 'Lot No'
    carat_columns = [
        'Carat 18', 'Carat 19', 'Carat 20', 
        'Carat 21', 'Carat 22', 'Carat 23', 'Carat 24'
    ]
    gross_weight_col = 'Gross Weight (gms)'
    location_col = 'Pouch location Branch Name'
    if lot_col not in df.columns:
        print(f"--- ERROR: Essential column '{lot_col}' not found. Aborting analysis. ---")
        return pd.DataFrame()

    # Ensure weight columns are numeric and fill empty cells with 0
    for col in carat_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    if location_col in df.columns:
        df[location_col] = df[location_col].astype(str)

    if gross_weight_col in df.columns:
        df[gross_weight_col] = pd.to_numeric(df[gross_weight_col], errors='coerce').fillna(0)
    else:
        df[gross_weight_col] = 0 # Create column if missing to prevent errors
        print(f"--- WARNING: Column '{gross_weight_col}' not found; gross weight will be 0. ---")

    # Group by Lot No and sum the carat columns
    existing_carat_columns = [col for col in carat_columns if col in df.columns]
    grouped_df = df.groupby(lot_col)[existing_carat_columns].sum()

    # Add total weight columns
    grouped_df['Total Calculated Net Weight'] = grouped_df[existing_carat_columns].sum(axis=1)
    grouped_df['Total Calc Gross Weight'] = df.groupby(lot_col)[gross_weight_col].sum()
    grouped_df['Location'] = df.groupby(lot_col)[location_col].first()
    
    print("--- SUCCESS: Weight analysis complete. ---")
    return grouped_df

if __name__ == "__main__":
    # Example for standalone testing
    test_file = r"C:\Users\Guest1\Workspace\gold_analysis\Samil_3-2-2026_12-33-48_PM_Inventory_List.xls"
    analysis_data = analyze_weights(test_file)
    if not analysis_data.empty:
        print("\n--- Standalone Test Result: ---")
        print(analysis_data.head())