import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

#Config
st.set_page_config(page_title="Airline Demand Dashboard", layout="wide")
API_KEY = "b44228311d0223cfcbda1d6f90c5b5d4"
API_URL = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&limit=100"

#Functions
@st.cache_data
def fetch_flight_data():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        st.error("Failed to fetch data from API")
        return []

def process_data(flights):
    df = pd.json_normalize(flights)
    df = df[[
        'airline.name',
        'flight.number',
        'departure.airport',
        'departure.scheduled',
        'arrival.airport',
        'arrival.scheduled'
    ]]
    df.rename(columns={
        'airline.name': 'Airline',
        'flight.number': 'Flight Number',
        'departure.airport': 'Departure Airport',
        'departure.scheduled': 'Departure Time',
        'arrival.airport': 'Arrival Airport',
        'arrival.scheduled': 'Arrival Time'
    }, inplace=True)
    
    #Drop rows with missing data
    df.dropna(inplace=True)
    
    #Parse date
    df['Departure Date'] = pd.to_datetime(df['Departure Time']).dt.date
    df['Route'] = df['Departure Airport'] + " → " + df['Arrival Airport']
    
    return df

#Main UI
st.title("✈️ Airline Booking Market Demand Dashboard")

with st.spinner("Fetching real-time flight data..."):
    flights = fetch_flight_data()
    if not flights:
        st.stop()
    df = process_data(flights)

#Display Data
st.subheader("📋 Flight Data")
st.dataframe(df.head(20), use_container_width=True)

#Route Analysis
st.subheader("🌐 Most Popular Routes")
top_routes = df['Route'].value_counts().head(10)
fig_routes = px.bar(
    x=top_routes.index,
    y=top_routes.values,
    labels={'x': 'Route', 'y': 'Number of Flights'},
    title="Top 10 Popular Routes"
)
st.plotly_chart(fig_routes, use_container_width=True)

#Demand Over Time
st.subheader("📅 High-Demand Departure Dates")
date_counts = df['Departure Date'].value_counts().sort_index()
fig_demand = px.line(
    x=date_counts.index,
    y=date_counts.values,
    labels={'x': 'Date', 'y': 'Flights'},
    title="Flight Volume by Departure Date"
)
st.plotly_chart(fig_demand, use_container_width=True)

#Filter
st.subheader("🔍 Filter by Airline")
airlines = df['Airline'].unique()
selected_airline = st.selectbox("Select an Airline", options=airlines)

filtered_df = df[df['Airline'] == selected_airline]
st.write(f"Showing {len(filtered_df)} flights for **{selected_airline}**.")
st.dataframe(filtered_df, use_container_width=True)

#Smart insights
st.subheader("🧠 Summary Insights")

top_routes = df['Route'].value_counts().head(3)

top_airline = df['Airline'].value_counts().idxmax()
airline_count = df['Airline'].value_counts().max()

busiest_day = df['Departure Date'].value_counts().idxmax()
busiest_day_count = df['Departure Date'].value_counts().max()

#Summary
summary = f"""
✅ **Top 3 busiest routes today:**
"""
for i, (route, count) in enumerate(top_routes.items(), start=1):
    summary += f"\n{i}. `{route}` — {count} flights"

summary += f"""

✅ **Most active airline:** `{top_airline}` with {airline_count} flights

✅ **Busiest day for departures:** `{busiest_day}` with {busiest_day_count} flights
"""

st.info(summary)