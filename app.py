import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="OLA Ride Insights",
    page_icon="🚕",
    layout="wide"
)

@st.cache_data
def load_data():
    data = pd.read_csv("OLA_Public_Data.csv")
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    for col in ["Booking_Value", "Ride_Distance",
                "Driver_Ratings", "Customer_Rating"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data

df = load_data()

st.title("🚕 OLA Ride Insights Dashboard")
st.caption("Explore booking trends, revenue, vehicles and ride performance.")

# Sidebar filters
st.sidebar.header("Filter Data")

vehicles = sorted(df["Vehicle_Type"].dropna().unique())
selected_vehicles = st.sidebar.multiselect(
    "Vehicle Type",
    vehicles,
    default=vehicles
)

statuses = sorted(df["Booking_Status"].dropna().unique())
selected_statuses = st.sidebar.multiselect(
    "Booking Status",
    statuses,
    default=statuses
)

payments = sorted(df["Payment_Method"].dropna().unique())
selected_payments = st.sidebar.multiselect(
    "Payment Method",
    payments,
    default=payments
)

filtered_df = df[
    df["Vehicle_Type"].isin(selected_vehicles)
    & df["Booking_Status"].isin(selected_statuses)
]

if selected_payments:
    filtered_df = filtered_df[
        filtered_df["Payment_Method"].isin(selected_payments)
        | filtered_df["Payment_Method"].isna()
    ]
else:
    filtered_df = filtered_df[
        filtered_df["Payment_Method"].isna()
    ]

# Completed rides
completed = filtered_df[
    (filtered_df["Booking_Status"] == "Success")
    & (filtered_df["Incomplete_Rides"] == "No")
]

# KPI metrics
total_bookings = len(filtered_df)
completed_rides = len(completed)
total_revenue = completed["Booking_Value"].sum()
avg_distance = completed["Ride_Distance"].mean()
avg_rating = completed["Customer_Rating"].mean()

st.subheader("Key Performance Indicators")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Bookings", f"{total_bookings:,}")
c2.metric("Completed Rides", f"{completed_rides:,}")
c3.metric("Total Revenue", f"₹{total_revenue:,.0f}")
c4.metric("Avg. Ride Distance", f"{avg_distance:.2f} km" if pd.notna(avg_distance) else "N/A")
c5.metric("Avg. Customer Rating", f"{avg_rating:.2f}/5" if pd.notna(avg_rating) else "N/A")

st.divider()

# Booking status chart
st.subheader("Booking Status Analysis")
status_data = filtered_df["Booking_Status"].value_counts().reset_index()
status_data.columns = ["Booking Status", "Bookings"]

fig1 = px.pie(
    status_data,
    names="Booking Status",
    values="Bookings",
    hole=0.45,
    title="Booking Status Distribution"
)
st.plotly_chart(fig1, use_container_width=True)

# Daily booking trend
st.subheader("Daily Booking Trend")
daily = (
    filtered_df.dropna(subset=["Date"])
    .groupby("Date")
    .size()
    .reset_index(name="Total Bookings")
)

fig2 = px.line(
    daily,
    x="Date",
    y="Total Bookings",
    markers=True,
    title="Bookings Over Time"
)
st.plotly_chart(fig2, use_container_width=True)

# Vehicle analysis
st.subheader("Vehicle Type Analysis")
vehicle_data = (
    completed.groupby("Vehicle_Type", as_index=False)
    .agg(
        Total_Ride_Distance=("Ride_Distance", "sum")
    )
)

fig3 = px.bar(
    vehicle_data,
    x="Vehicle_Type",
    y="Total_Ride_Distance",
    title="Total Ride Distance by Vehicle Type",
    labels={"Total_Ride_Distance": "Ride Distance (km)"}
)
st.plotly_chart(fig3, use_container_width=True)

# Revenue analysis
st.subheader("Revenue Analysis")
revenue_data = (
    completed.groupby("Payment_Method", as_index=False)["Booking_Value"]
    .sum()
)

fig4 = px.bar(
    revenue_data,
    x="Payment_Method",
    y="Booking_Value",
    title="Revenue by Payment Method",
    labels={"Booking_Value": "Revenue (₹)"}
)
st.plotly_chart(fig4, use_container_width=True)

# Ratings analysis
st.subheader("Customer Ratings by Vehicle Type")
rating_data = (
    completed.groupby("Vehicle_Type", as_index=False)["Customer_Rating"]
    .mean()
)

fig5 = px.bar(
    rating_data,
    x="Vehicle_Type",
    y="Customer_Rating",
    title="Average Customer Rating by Vehicle Type",
    labels={"Customer_Rating": "Average Rating"}
)
st.plotly_chart(fig5, use_container_width=True)

st.success("OLA Ride Insights dashboard loaded successfully!")
st.caption("Data source: OLA_Cleaned_Data.csv")
