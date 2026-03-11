import pandas as pd
import re

def extract_lot_prices(file_path):
    """Extracts Lot or Loan numbers and their corresponding prices from the 'Rates' sheet."""
    try:
        df = pd.read_excel(file_path, sheet_name='Rates', header=None)
    except Exception as e:
        print(f"--- WARNING: Could not read 'Rates' sheet: {e}. Price data missing. ---")
        return pd.DataFrame(columns=['Lot No', 'Bid Starting Price'])

    extracted_data = []
    current_active_lot = None

    for index, row in df.iterrows():
        row_list = [str(val).strip() for val in row.tolist() if str(val).lower() != 'nan']
        row_text = " ".join(row_list)
        upper_text = row_text.upper()

        # 1. DYNAMIC SEARCH FOR ID (Matches "LOT:Lot123" OR "Loan Number:123456")
        if "LOT:" in upper_text or "LOAN NUMBER:" in upper_text:
            
            # Try to match the original Lot format
            lot_match = re.search(r'(Lot\d+)', row_text, re.IGNORECASE)
            # Try to match the new Loan format (extracts the digits)
            loan_match = re.search(r'Loan Number:\s*(\d+)', row_text, re.IGNORECASE)

            if lot_match:
                current_active_lot = lot_match.group(1)
            elif loan_match:
                current_active_lot = loan_match.group(1)

        # 2. SEARCH FOR PRICE ONLY IF AN ID IS ACTIVE
        if current_active_lot and ("Current Price" in row_text or "Next Valid Bid" in row_text):
            price_match = re.search(r'₹\s?([\d,]+)', row_text)
            if price_match:
                clean_price = price_match.group(1).replace(',', '')
                try:
                    price_val = float(clean_price)
                    extracted_data.append({
                        'Lot No': current_active_lot, # Always save as 'Lot No' to match main sheet
                        'Bid Starting Price': price_val
                    })
                    current_active_lot = None 
                except ValueError:
                    continue

    if extracted_data:
        final_df = pd.DataFrame(extracted_data)
        print(f"--- SUCCESS: Extracted {len(final_df)} prices. ---")
        return final_df
    else:
        return pd.DataFrame(columns=['Lot No', 'Bid Starting Price'])