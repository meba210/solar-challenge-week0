import pandas as pd
import os
import streamlit as st 
import plotly.graph_objects as go

def load_data():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    data_dir = os.path.join(base_dir, 'data')

    # Load and tag each country's dataset
    benin = pd.read_csv(os.path.join(data_dir, "benin_clean.csv"))
    benin["country"] = "Benin"


    sierraleone = pd.read_csv(os.path.join(data_dir, "sierraleone_clean.csv"))
    sierraleone["country"] = "Sierra Leone"

    togo = pd.read_csv(os.path.join(data_dir, "togo_clean.csv"))
    togo["country"] = "Togo"

    # Combine them into one DataFrame
    df = pd.concat([benin, sierraleone, togo], ignore_index=True)

    # Normalize column names for consistency
    df.columns = df.columns.str.strip().str.lower()

    # Rename likely region/GHI column variants to standard names
    rename_map = {}
    for col in df.columns:
        if col in ['region name', 'region', 'adm1', 'admin1']:
            rename_map[col] = 'region'
        if col in ['ghi', 'ghi (kwh/m²/day)', 'global horizontal irradiation']:
            rename_map[col] = 'ghi'

    df = df.rename(columns=rename_map)

    return df

def top_regions_table(df):
    if 'ws' not in df.columns or 'ghi' not in df.columns:
        raise KeyError("Required columns 'ws' or 'ghi' not found.")

    return (
        df.groupby("ws")["ghi"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
        .head(10)
    )

def filter_numeric_range(df, column, label):
    if column in df.columns:
        min_val = float(df[column].min())
        max_val = float(df[column].max())
        selected_range = st.sidebar.slider(
            f"Filter by {label}",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val),
            step=(max_val - min_val) / 100,
            format="%.2f"
        )
        return df[(df[column] >= selected_range[0]) & (df[column] <= selected_range[1])]
    else:
        return df
    

def plot_variable_pie(df, column, label, color, donut=False):
    if column not in df.columns:
        return

    # Bin the values for pie chart categories
    binned = pd.cut(df[column], bins=5)
    counts = binned.value_counts().sort_index()

    labels = [f"{interval.left:.1f} - {interval.right:.1f}" for interval in counts.index]
    values = counts.values

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4 if donut else 0.0,
        marker=dict(colors=[color]*len(values)),
        textinfo='label+percent'
    )])

    fig.update_layout(title_text=f"{label} Distribution", margin=dict(t=40, b=20))

    st.plotly_chart(fig, use_container_width=True)    