import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Konfiguration
API_BASE_URL = "http://localhost:8000"
REFRESH_INTERVAL = 30  # sekunder

st.set_page_config(page_title="Smart Väderstation", page_icon="🌤️", layout="wide")


def fetch_latest_data():
    """Hämta senaste datapunkt från API"""
    try:
        response = requests.get(f"{API_BASE_URL}/data/latest")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Kunde inte hämta data: {e}")
    return None


def fetch_history(hours=24):
    """Hämta historisk data"""
    try:
        response = requests.get(f"{API_BASE_URL}/data/history?hours={hours}")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Kunde inte hämta historik: {e}")
    return []


def fetch_statistics():
    """Hämta statistik"""
    try:
        response = requests.get(f"{API_BASE_URL}/data/stats")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Kunde inte hämta statistik: {e}")
    return {}


def main():
    st.title("🌤️ Smart Väderstation")
    st.markdown("Realtidsövervakning av temperatur, fuktighet och ljusnivå")

    # Auto-uppdatering
    if st.checkbox("Auto-uppdatering", value=True):
        time.sleep(REFRESH_INTERVAL)
        st.rerun()

    # Hämta data
    latest_data = fetch_latest_data()
    history_data = fetch_history()
    stats = fetch_statistics()

    if not latest_data:
        st.warning("Ingen data tillgänglig från sensorer")
        return

    # Visa senaste mätvärden
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Temperatur",
            value=f"{latest_data['temperature']:.1f}°C",
            delta=f"{stats.get('avg_temperature', 0):.1f}°C snitt",
        )

    with col2:
        st.metric(
            label="Luftfuktighet",
            value=f"{latest_data['humidity']:.1f}%",
            delta=f"{stats.get('avg_humidity', 0):.1f}% snitt",
        )

    with col3:
        st.metric(
            label="Ljusnivå",
            value=f"{latest_data['light_level']:.1f}%",
            delta=f"{stats.get('avg_light', 0):.1f}% snitt",
        )

    # Konvertera historik till DataFrame
    if history_data:
        df = pd.DataFrame(history_data)
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

        # Skapa diagram
        st.subheader("Tidsseriediagram")

        # Temperatur och fuktighet
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["temperature"],
                name="Temperatur (°C)",
                line=dict(color="red", width=2),
            )
        )
        fig1.add_trace(
            go.Scatter(
                x=df["datetime"],
                y=df["humidity"],
                name="Fuktighet (%)",
                yaxis="y2",
                line=dict(color="blue", width=2),
            )
        )

        fig1.update_layout(
            title="Temperatur och Luftfuktighet",
            xaxis_title="Tid",
            yaxis=dict(title="Temperatur (°C)", side="left"),
            yaxis2=dict(title="Fuktighet (%)", side="right", overlaying="y"),
            hovermode="x unified",
        )

        st.plotly_chart(fig1, use_container_width=True)

        # Ljusnivå
        fig2 = px.line(df, x="datetime", y="light_level", title="Ljusnivå över tid")
        fig2.update_layout(yaxis_title="Ljusnivå (%)")
        st.plotly_chart(fig2, use_container_width=True)

        # Visa rådata
        st.subheader("Rådata")
        st.dataframe(
            df[["datetime", "temperature", "humidity", "light_level"]].sort_values(
                "datetime", ascending=False
            )
        )

    # Visa statistik
    if stats:
        st.subheader("Statistik (senaste 24h)")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.info(f"**Datapunkter:** {stats.get('data_points', 0)}")

        with col2:
            st.info(f"**Max temp:** {stats.get('max_temperature', 0):.1f}°C")

        with col3:
            st.info(f"**Min temp:** {stats.get('min_temperature', 0):.1f}°C")

        with col4:
            st.info(f"**Snitt temp:** {stats.get('avg_temperature', 0):.1f}°C")


if __name__ == "__main__":
    main()
