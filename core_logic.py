import pandas as pd

def apply_business_logic(df, gold_rate_18k, office_location):
    """
    Enhanced Logic:
    1. Gold Valuation (18K + 3% GST)
    2. Travel/Proximity Deduction (Vellore base)
    3. Stone/Sand Warning (Gross vs Net diff)
    """
    # Ensure numeric types
    df['Bid Starting Price'] = pd.to_numeric(df['Bid Starting Price'], errors='coerce')
    df['Total Calculated Net Weight'] = pd.to_numeric(df['Total Calculated Net Weight'], errors='coerce')
    df['Total Calc Gross Weight'] = pd.to_numeric(df['Total Calc Gross Weight'], errors='coerce')

    # --- 1. Basic Valuation ---
    df['Market Value (18K)'] = df['Total Calculated Net Weight'] * gold_rate_18k
    # We add 3% GST to the value because that is an additional cost you pay on the bid
    df['Max Bid Threshold (Incl GST)'] = df['Market Value (18K)'] * 1.03

    # --- 2. Travel & Proximity Logic ---
    # Estimated travel cost per km (fuel + time) from Vellore
    # Example distances from Vellore: Chennai (~140km), Chengalpattu (~120km)
    def calculate_travel_cost(branch_name):
        branch = str(branch_name).lower()
        if 'chennai' in branch: return 3000
        if 'chengalpattu' in branch: return 2500
        if 'vellore' in branch: return 500
        return 4000 # Default for unknown/far locations

    # Check if 'Branch Name' exists in your merged dataframe
    if 'Location' in df.columns:
        df['Travel Cost'] = df['Location'].apply(calculate_travel_cost)
    else:
        df['Travel Cost'] = 2000 # Flat average if location missing

    # --- 3. Net Profit Calculation ---
    # Profit = (Market Value - Travel) - Bid Price
    df['Adjusted Profit Margin'] = (df['Max Bid Threshold (Incl GST)'] - df['Travel Cost']) - df['Bid Starting Price']

    # --- 4. Stone/Sand Warning Logic ---
    # If Gross weight is significantly higher than Net weight (e.g., > 15% difference)
    def check_stones(row):
        if row['Total Calc Gross Weight'] > 0:
            diff_ratio = (row['Total Calc Gross Weight'] - row['Total Calculated Net Weight']) / row['Total Calc Gross Weight']
            if diff_ratio > 0.15: # 15% threshold
                return "⚠️ HIGH STONE RISK: Weight diff > 15%"
        return "Normal"

    df['Stone Warning'] = df.apply(check_stones, axis=1)

    # --- 5. Final Decision ---
    def final_decision(row):
        if pd.isna(row['Bid Starting Price']): return "Skip: No Price"
        if row['Adjusted Profit Margin'] < 15000: return "DONT TOUCH"
        # if row['Adjusted Profit Margin'] > 15000: return "🔥 POTENTIAL HIGH PROFIT"
        return "Biddable"

    df['Auction Decision'] = df.apply(final_decision, axis=1)
    
    return df