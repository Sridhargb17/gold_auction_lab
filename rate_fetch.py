import pandas as pd
import re

def extract_lot_prices(file_path):
    """Extracts Lot numbers and their corresponding prices from the 'Rates' sheet."""
    try:
        # Load raw grid from the 'Rates' sheet
        df = pd.read_excel(file_path, sheet_name='Rates', header=None)
    except Exception as e:
        print(f"--- WARNING: Could not read 'Rates' sheet: {e}. Price data will be missing. ---")
        return pd.DataFrame(columns=['Lot No', 'Bid Starting Price'])

    extracted_data = []
    current_active_lot = None

    for index, row in df.iterrows():
        # Clean row data and join into a single string for pattern matching
        row_list = [str(val).strip() for val in row.tolist() if str(val).lower() != 'nan']
        row_text = " ".join(row_list)

        # 1. SEARCH FOR LOT ID (Preserving 'LotXXXX' format)
        if "LOT:" in row_text.upper():
            # Matches 'Lot' followed by numbers, ignoring case
            lot_match = re.search(r'(Lot\d+)', row_text, re.IGNORECASE)
            if lot_match:
                # We take the exact string found (e.g., "Lot2441")
                current_active_lot = lot_match.group(1)

        # 2. SEARCH FOR PRICE ONLY IF A LOT IS ACTIVE
        # If a lot is active, look for a price. Use "Next Valid Bid" as a fallback if "Current Price" is empty.
        if current_active_lot and ("Current Price" in row_text or "Next Valid Bid" in row_text):
            # Extract digits and commas associated with the currency symbol
            price_match = re.search(r'₹\s?([\d,]+)', row_text)
            if price_match:
                clean_price = price_match.group(1).replace(',', '')
                try:
                    price_val = float(clean_price)
                    extracted_data.append({
                        'Lot No': current_active_lot, 
                        'Bid Starting Price': price_val
                    })
                    # Reset active lot to ensure clean pairing for the next block
                    current_active_lot = None 
                except ValueError:
                    continue

    # Finalize and return the DataFrame
    if extracted_data:
        final_df = pd.DataFrame(extracted_data)
        print(f"--- SUCCESS: Extracted {len(final_df)} lot prices. ---")
        return final_df
    else:
        print("--- WARNING: No lot prices found in 'Rates' sheet. ---")
        return pd.DataFrame(columns=['Lot No', 'Bid Starting Price'])

if __name__ == "__main__":
    # Example for standalone testing
    test_file = r"C:\Users\Guest1\Workspace\gold_analysis\Samil_3-2-2026_12-33-48_PM_Inventory_List.xls"
    rates_data = extract_lot_prices(test_file)
    if not rates_data.empty:
        print("\n--- Standalone Test Result: ---")
        print(rates_data.head())