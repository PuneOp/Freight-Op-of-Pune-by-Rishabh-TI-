import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- Configuration ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1e0hMmMTqhZlSutnrfRgxX3GHrqX1HkuobA_YLXvC-yo/edit#gid=976860178"

st.set_page_config(page_title="Railway Performance Dashboard", layout="wide")

# --- Styling ---
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stMetric { background-color: #FFFFFF; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- Data Fetching ---
@st.cache_data(ttl=3600)
def load_data():
    csv_url = SHEET_URL.replace('/edit#gid=', '/export?format=csv&gid=')
    # Read raw
    raw_df = pd.read_csv(csv_url)

    # Extract Table 1
    t1 = raw_df.iloc[0:13, 0:13].copy()
    t1.columns = ["Month", "2022-23", "2023-24", "2024-25", "2025-26", "2026-27", "% Var", "Cumm 22-23", "Cumm 23-24", "Cumm 24-25", "Cumm 25-26", "Cumm 26-27", "Cumm % Var"]
    t1 = t1.drop(0)

    # Extract Table 2
    t2 = raw_df.iloc[16:29, 0:13].copy()
    t2.columns = ["Month", "2022-23", "2023-24", "2024-25", "2025-26", "2026-27", "% Var", "Cumm 22-23", "Cumm 23-24", "Cumm 24-25", "Cumm 25-26", "Cumm 26-27", "Cumm % Var"]

    return {"Including": t1, "Excluding": t2}

try:
    data_dict = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Sidebar ---
st.sidebar.title("Dashboard Controls")
metric_type = st.sidebar.selectbox("Select Speed Type", ["Including", "Excluding"])
df = data_dict[metric_type]
year_selection = st.sidebar.selectbox("Select Year", ["2022-23", "2023-24", "2024-25", "2025-26", "2026-27"])

# --- Main Dashboard ---
st.title("📊 Railway Performance Dashboard")
st.markdown(f"### {metric_type} Stabling & Yarding | Analyzing: {year_selection}")

# Ensure numeric
for col in ["2022-23", "2023-24", "2024-25", "2025-26", "2026-27"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')
for col in ["Cumm 22-23", "Cumm 23-24", "Cumm 24-25", "Cumm 25-26", "Cumm 26-27"]:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Logic for Month vs LY Month
latest_month_idx = df['Month'].dropna().index[-1]
current_val = df.loc[latest_month_idx, year_selection]
prev_year_col = f"{int(year_selection[:4])-1}-{int(year_selection[5:])-1}"
prev_val = df.loc[latest_month_idx, prev_year_col] if prev_year_col in df.columns else 0

delta = ((current_val - prev_val) / prev_val) * 100 if prev_val != 0 else 0

col1, col2 = st.columns(2)
with col1:
    st.metric(label=f"{df.loc[latest_month_idx, 'Month']} Performance",
              value=f"{current_val:.2f} KMPH", delta=f"{delta:.2f}% (vs LY)")

# Logic for Upto Month
cumm_col = f"Cumm {year_selection}"
prev_cumm_col = f"Cumm {prev_year_col}"
cumm_val = df.loc[latest_month_idx, cumm_col]
prev_cumm_val = df.loc[latest_month_idx, prev_cumm_col] if prev_cumm_col in df.columns else 0
cumm_delta = ((cumm_val - prev_cumm_val) / prev_cumm_val) * 100 if prev_cumm_val != 0 else 0

with col2:
    st.metric(label=f"Upto {df.loc[latest_month_idx, 'Month']} Cumulative",
              value=f"{cumm_val:.2f} KMPH", delta=f"{cumm_delta:.2f}% (vs LY)")

st.subheader("Monthly Trend")
fig = px.line(df, x='Month', y=[year_selection, prev_year_col], markers=True)
st.plotly_chart(fig, use_container_width=True)


