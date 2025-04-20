import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("superstore_uptd.csv", parse_dates=["Order Date"])
    df["Year"] = df["Order Date"].dt.year
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filters")
start_date, end_date = st.sidebar.date_input("Select Date Range", [df["Order Date"].min(), df["Order Date"].max()])
selected_states = st.sidebar.selectbox("Select State", ["All"] + list(df["State"].unique()))
filtered_cities = df[df["State"] == selected_states]["City"].unique() if selected_states != "All" else df["City"].unique()
selected_cities = st.sidebar.selectbox("Select City", ["All"] + list(filtered_cities))

df = df[(df["Order Date"] >= pd.to_datetime(start_date)) & (df["Order Date"] <= pd.to_datetime(end_date))]
if selected_states != "All":
    df = df[df["State"] == selected_states]
if selected_cities != "All":
    df = df[df["City"] == selected_cities]

# Dashboard Title
st.title("Sales & Profit Dashboard")

# Pie Chart - Segment Distribution
st.subheader("Product Name Count by Segment")
segment_counts = df["Segment"].value_counts().reset_index()
segment_counts.columns = ["Segment", "Count"]
fig_pie = px.pie(segment_counts, values="Count", names="Segment", title="Segment Distribution", hole=0.3)
fig_pie.update_traces(marker=dict(line=dict(color='#000000', width=2)), pull=[0.1, 0.1, 0.1], textinfo='percent+label')
st.plotly_chart(fig_pie)

# Pie Chart - Shipping Mode Frequency
st.subheader("Shipping Mode Frequency")
ship_mode_counts = df["Ship Mode"].value_counts().reset_index()
ship_mode_counts.columns = ["Ship Mode", "Count"]
fig_ship_pie = px.pie(ship_mode_counts, values="Count", names="Ship Mode", title="Shipping Mode Distribution", hole=0.3)
fig_ship_pie.update_traces(marker=dict(line=dict(color='#000000', width=2)), pull=[0.1, 0.1, 0.1], textinfo='percent+label')
st.plotly_chart(fig_ship_pie)

# Line Chart - Cumulative Sales & Profit Over Time
st.subheader("Cumulative Sales & Profit Over Time")
df_sorted = df.sort_values("Order Date")
df_sorted["Cumulative Sales"] = df_sorted["Sales"].cumsum()
df_sorted["Cumulative Profit"] = df_sorted["Profit"].cumsum()
fig_cum = px.line(df_sorted, x="Order Date", y=["Cumulative Sales", "Cumulative Profit"], title="Cumulative Sales & Profit")
st.plotly_chart(fig_cum)

# Heatmap - Sales vs. Discount with Improved Color Scheme
st.subheader("Discount vs Sales Heatmap")
fig_heatmap = px.density_heatmap(
    df, 
    x="Discount", 
    y="Sales", 
    title="Impact of Discount on Sales", 
    color_continuous_scale="peach"
)
fig_heatmap.update_layout(
    yaxis=dict(range=[0, 5000]), 
    font=dict(color="white")  # White font for better readability
)
st.plotly_chart(fig_heatmap)

# Treemap - Category & Subcategory Breakdown with Enhanced Hover Labels
st.subheader("Sales Distribution by Category & Subcategory")
fig_treemap = px.treemap(df, path=["Category", "Sub-Category"], values="Sales", title="Category & Subcategory Sales Breakdown", hover_data={"Sales":":.2f"})
st.plotly_chart(fig_treemap)

# Bar Chart - Sales by Product Name and Category (Removing Outliers)
st.subheader("Total Sales by Product Name and Category")
category_sales = df.groupby(["Category", "Product Name"]).agg({"Sales": "sum"}).reset_index()
q1 = category_sales["Sales"].quantile(0.25)
q3 = category_sales["Sales"].quantile(0.75)
iqr = q3 - q1
upper_bound = q3 + 1.5 * iqr
filtered_category_sales = category_sales[category_sales["Sales"] <= upper_bound]
fig_bar = px.bar(filtered_category_sales, x="Product Name", y="Sales", color="Category", title="Sales by Product")
st.plotly_chart(fig_bar)

# Gauge Chart - Maximum Profit
st.subheader("Maximum Profit in Dollars")
max_profit = df["Profit"].max()
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=max_profit,
    title={"text": "Maximum Profit"},
    gauge={"axis": {"range": [0, max_profit * 2]}}
))
st.plotly_chart(fig_gauge)

# Stacked Bar Chart - Total Sales by State and Category
st.subheader("Total Sales by State and Category")
state_category_sales = df.groupby(["State", "Category"]).agg({"Sales": "sum"}).reset_index()
fig_state_sales = px.bar(state_category_sales, x="State", y="Sales", color="Category", title="Sales by State", barmode='stack')
st.plotly_chart(fig_state_sales)
