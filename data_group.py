import pandas as pd

def analyze_weights(file_path):
    """Groups inventory by Lot/Loan No and calculates net and gross weight totals."""
    try:
        df = pd.read_excel(file_path, header=0, sheet_name=0)
    except Exception as e:
        print(f"--- ERROR: Could not read the main inventory sheet: {e} ---")
        return pd.DataFrame()

    df.columns = df.columns.astype(str).str.strip()

    # --- NEW DYNAMIC ID DETECTION ---
    primary_id_col = 'Lot No'
    fallback_id_col = 'Loan Account No'

    if primary_id_col in df.columns:
        active_id_col = primary_id_col
    elif fallback_id_col in df.columns:
        active_id_col = fallback_id_col
        # Rename it internally so downstream logic stays identical
        df.rename(columns={fallback_id_col: primary_id_col}, inplace=True)
    else:
        print(f"--- ERROR: Neither '{primary_id_col}' nor '{fallback_id_col}' found. ---")
        return pd.DataFrame()
    # --------------------------------

    carat_columns = [
        'Carat 18', 'Carat 19', 'Carat 20', 
        'Carat 21', 'Carat 22', 'Carat 23', 'Carat 24'
    ]
    gross_weight_col = 'Gross Weight (gms)'
    location_col = 'Pouch location Branch Name'

    for col in carat_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    if location_col in df.columns:
        df[location_col] = df[location_col].astype(str)

    if gross_weight_col in df.columns:
        df[gross_weight_col] = pd.to_numeric(df[gross_weight_col], errors='coerce').fillna(0)
    else:
        df[gross_weight_col] = 0

    existing_carat_columns = [col for col in carat_columns if col in df.columns]
    
    # Grouping using the standardized column
    grouped_df = df.groupby(primary_id_col)[existing_carat_columns].sum()
    grouped_df['Total Calculated Net Weight'] = grouped_df[existing_carat_columns].sum(axis=1)
    grouped_df['Total Calc Gross Weight'] = df.groupby(primary_id_col)[gross_weight_col].sum()
    
    if location_col in df.columns:
        grouped_df['Location'] = df.groupby(primary_id_col)[location_col].first()
    
    return grouped_df