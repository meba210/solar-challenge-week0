import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
from app.utils import load_data, top_regions_table, plot_variable_pie

st.set_page_config(
    page_title="GHI Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
df = load_data()

# Sidebar
st.sidebar.title("☀️ Solar GHI Dashboard")
st.sidebar.markdown("---")

if "country" not in df.columns:
    st.error("Column 'country' not found in dataset.")
    st.stop()

# Country filter
country = st.sidebar.selectbox("🌍 Select Country", options=df["country"].unique())
filtered_df = df[df["country"] == country]

# Additional filters for ModA, ModB, Tamb, RH (if present)

# filtered_df = filter_numeric_range(filtered_df, "moda", "ModA (W/m²)")
# filtered_df = filter_numeric_range(filtered_df, "modb", "ModB (W/m²)")
# filtered_df = filter_numeric_range(filtered_df, "tamb", "Ambient Temperature (°C)")
# filtered_df = filter_numeric_range(filtered_df, "rh", "Relative Humidity (%)")

# Page Title
st.title(f"📊 Solar Insights - {country}")

# Layout: Top GHI Table and Summary
with st.container():
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("🔥 Top 10 Wind Speeds by Avg GHI")
        try:
            top_regions = top_regions_table(filtered_df)
            st.dataframe(top_regions, use_container_width=True)
        except KeyError as e:
            st.error(f"Error: {e}")

    with col2:
        st.metric("Total Records", len(filtered_df))
        st.metric("Average GHI", f"{filtered_df['ghi'].mean():.2f} kWh/m²/day" if not filtered_df.empty else "N/A")

# GHI Distribution Histogram
with st.container():
    st.subheader("📈 GHI Distribution")
    fig = px.histogram(filtered_df, x="ghi", nbins=30, title="Distribution of GHI Values",
                       color_discrete_sequence=["#00cc96"])
    st.plotly_chart(fig, use_container_width=True)

# GHI by Region Bar Chart
with st.container():
    st.subheader("🏙️ Average Global Horizontal Irradiance, by Region")
    if "country" in filtered_df.columns:
        region_avg = filtered_df.groupby("country")["ghi"].mean().reset_index()
        fig2 = px.bar(region_avg, x="country", y="ghi", title="Average GHI by Region",
                      color="ghi", color_continuous_scale="sunset", height=500)
        fig2.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No 'region' column available for plotting.")

# Area Chart by Wind Speed Buckets (GHI Contribution)
with st.container():
    st.subheader("🌪️ Wind Speed Bucket Area Chart (GHI Contribution)")
    if "ws" in filtered_df.columns:
        bins = [0, 1, 2, 3, 4, 5, 6, 7, 100]
        labels = ['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7+']
        filtered_df["wind_bucket"] = pd.cut(filtered_df["ws"], bins=bins, labels=labels)

        wind_ghi = filtered_df.groupby("wind_bucket")["ghi"].sum().reset_index()

        # Sort wind_bucket properly (in case categorical ordering is lost)
        wind_ghi["wind_bucket"] = pd.Categorical(wind_ghi["wind_bucket"], categories=labels, ordered=True)
        wind_ghi = wind_ghi.sort_values("wind_bucket")

        fig_area = px.area(
            wind_ghi,
            x="wind_bucket",
            y="ghi",
            title="GHI by Wind Speed Bucket (Area Chart)",
            labels={"wind_bucket": "Wind Speed Bucket (m/s)", "ghi": "Total GHI (kWh/m²/day)"},
            line_shape="spline",
            color_discrete_sequence=["#636efa"]
        )
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.warning("Column 'ws' (wind speed) not found.")



def plot_variable_distribution(df, variable, label, color):
    if variable in df.columns and not df[variable].isna().all():
        st.subheader(f"📊 {label} Distribution")
        fig = px.histogram(df, x=variable, nbins=30, title=f"Distribution of {label}",
                           color_discrete_sequence=[color])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Column '{variable}' not found or empty.")

def plot_variable_vs_ghi(df, variable, label, color):
    if variable in df.columns and "ghi" in df.columns and not df.empty:
        st.subheader(f"📈 {label} vs GHI")
        fig = px.scatter(df, x=variable, y="ghi", title=f"{label} vs GHI",
                         color_discrete_sequence=[color], trendline="ols")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Required columns '{variable}' or 'ghi' not found or data empty.")

with st.container():
    plot_variable_pie(filtered_df, "moda", "ModA (W/m²)", "#F45B69", donut=True)
    plot_variable_pie(filtered_df, "modb", "ModB (W/m²)", "#2ED8B6", donut=False)
    plot_variable_pie(filtered_df, "tamb", "Ambient Temperature (°C)", "#4C78A8", donut=True)
    plot_variable_pie(filtered_df, "rh", "Relative Humidity (%)", "#A074C4", donut=False)


# Raw data preview
with st.expander("🔍 Raw Data Preview"):
    st.dataframe(filtered_df.head(20), use_container_width=True)
