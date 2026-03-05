import streamlit as st
import pandas as pd
import os
from main import run_pipeline

st.set_page_config(page_title="Gold Auction Decision Tool", layout="wide")

# FIX: Corrected the keyword argument to unsafe_allow_html
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Gold Auction Decision Support")

with st.sidebar:
    st.header("Live Market Config")
    # Using the 18K rate found in your Chennai screenshot
    rate_18k = st.number_input("Today's 18K Rate (₹/g)", value=13100) 
    office = st.selectbox("Office Location", ["Vellore", "Chennai"])
    st.info("Logic: Evaluating all lots as 18K + 3% GST + Travel from Vellore.")

uploaded_file = st.file_uploader("Upload Samil Inventory XLS", type=['xls', 'xlsx'])

if uploaded_file:
    temp_path = "temp_inventory.xls"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button("Run Auction Analysis"):
        df = run_pipeline(temp_path, rate_18k, office)
        
        if not df.empty:
            # Metric Summary
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Lots", len(df))
            c2.metric("Biddable Items", len(df[df['Auction Decision'] == "Biddable"]))
            # High stone risk check
            risk_count = len(df[df['Stone Warning'].str.contains("HIGH")])
            c3.metric("High Stone Risk", risk_count)

            # Styled Results Table
            st.write("### Analysis Results")
            st.dataframe(df)
            
            st.download_button("Download Report", df.to_csv(index=False), "Auction_Decision_Report.csv")
        else:
            st.error("No data extracted. Verify file format.")