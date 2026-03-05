import streamlit as st
import pandas as pd
import os
from main import run_pipeline

st.set_page_config(page_title="Gold Auction Decision Tool", layout="wide")

# FIX 1: Dark Mode Compatibility
# Using var(--secondary-background-color) so it adapts to light/dark themes natively
st.markdown("""
    <style>
    .stMetric { 
        background-color: var(--secondary-background-color); 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Gold Auction Decision Support")

with st.sidebar:
    st.header("Live Market Config")
    rate_18k = st.number_input("Today's 18K Rate (₹/g)", value=13100) 
    office = st.selectbox("Office Location", ["Vellore", "Chennai"])
    st.info("Logic: Evaluating all lots as 18K + 3% GST + Travel from Vellore.")

uploaded_file = st.file_uploader("Upload Samil Inventory XLS", type=['xls', 'xlsx'])

if uploaded_file:
    temp_path = "temp_inventory.xls"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("Run Auction Analysis"):
        with st.spinner("Analyzing weights and prices..."):
            # We save the processed data into session_state. 
            # This prevents the data from disappearing when you interact with the filters.
            st.session_state['report_data'] = run_pipeline(temp_path, rate_18k, office)

# FIX 2: Interactive Filtering
# Only show the dashboard if data has been processed and saved in the session state
if 'report_data' in st.session_state:
    df = st.session_state['report_data']
    
    if not df.empty:
        # 1. Metric Summary
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Lots", len(df))
        c2.metric("Biddable Items", len(df[df['Auction Decision'] == "Biddable"]))
        risk_count = len(df[df['Stone Warning'].str.contains("HIGH")])
        c3.metric("High Stone Risk", risk_count)

        st.write("---")
        
        # 2. Filter Toggles (Since metrics aren't natively clickable)
        filter_choice = st.radio(
            "Filter Table View:", 
            ["Show All Lots", "Biddable Items Only", "High Stone Risk Only"], 
            horizontal=True
        )
        
        # 3. Apply Filter Logic
        display_df = df.copy()
        if filter_choice == "Biddable Items Only":
            display_df = display_df[display_df['Auction Decision'] == "Biddable"]
        elif filter_choice == "High Stone Risk Only":
            display_df = display_df[display_df['Stone Warning'].str.contains("HIGH")]

        # -> NEW: Sort the data by Adjusted Profit Margin from High to Low
        if 'Adjusted Profit Margin' in display_df.columns:
            display_df = display_df.sort_values(by='Adjusted Profit Margin', ascending=False)

        # 4. Show Filtered Table
        st.write(f"### Results: {filter_choice}")
        st.dataframe(display_df)
        
        # Ensure the downloaded file matches what is currently filtered and sorted
        st.download_button(
            label=f"Download {filter_choice} as CSV", 
            data=display_df.to_csv(index=False), 
            file_name="Filtered_Auction_Report.csv"
        )
    else:
        st.error("No data extracted. Verify file format.")