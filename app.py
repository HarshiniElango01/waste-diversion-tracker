import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="EcoTrack Enterprise", layout="wide", page_icon="♻️")

# Custom CSS for "Professional" Look
st.markdown("""
    <style>
    .big-font { font-size:20px !important; }
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #4CAF50; }
    </style>
    """, unsafe_allow_html=True)

# File to store data
DATA_FILE = "waste_data.csv"

# --- 2. HELPER FUNCTIONS ---
def load_data():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame({
            "Date": [datetime.now().date() - timedelta(days=i*7) for i in range(5)],
            "Recycling": [45, 48, 50, 52, 40],
            "Compost": [20, 22, 25, 28, 15],
            "Landfill": [100, 95, 90, 85, 110]
        })
        df.to_csv(DATA_FILE, index=False)
    return pd.read_csv(DATA_FILE)

def save_entry(recycling, compost, landfill):
    df = load_data()
    new_entry = pd.DataFrame({
        "Date": [datetime.now().date()],
        "Recycling": [recycling],
        "Compost": [compost],
        "Landfill": [landfill]
    })
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return df

def get_waste_advice(item):
    item = item.lower().strip()
    database = {
        "pizza box": "Compost (if greasy) / Recycle (if clean)",
        "plastic bottle": "Recycle (Rinse first)",
        "banana peel": "Compost",
        "styrofoam": "Landfill (Avoid usage!)",
        "aluminum foil": "Recycle (Clean)",
        "batteries": "E-Waste Drop-off (Do not bin)",
        "coffee cup": "Landfill (Lined with plastic) / Lid is Recyclable",
        "glass jar": "Recycle"
    }
    for key in database:
        if key in item:
            return database[key]
    return "Unknown item. General rule: When in doubt, throw it out (Landfill)."

# --- 3. SIDEBAR NAVIGATION ---
# REPLACED IMAGE WITH EMOJI HERE
st.sidebar.markdown("# ♻️ EcoTrack") 
menu = st.sidebar.radio(
    "Navigate", 
    ["📊 Executive Dashboard", "📝 Daily Logger", "🔍 Smart Sorter", "🔮 AI Analyst", "🏆 Gamification"]
)
st.sidebar.info("v2.0 - Capstone Build")

# --- 4. MAIN PAGES ---
df = load_data()

# === PAGE 1: DASHBOARD ===
if menu == "📊 Executive Dashboard":
    st.title("📊 Executive Dashboard")
    st.markdown("Overview of waste diversion performance.")

    total_recycling = df['Recycling'].sum()
    total_compost = df['Compost'].sum()
    total_landfill = df['Landfill'].sum()
    grand_total = total_recycling + total_compost + total_landfill
    
    if grand_total > 0:
        div_rate = ((total_recycling + total_compost) / grand_total) * 100
    else:
        div_rate = 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Waste Logged", f"{grand_total} kg", "All time")
    col2.metric("Landfill", f"{total_landfill} kg", "-Bad")
    col3.metric("Diverted (Good)", f"{total_recycling + total_compost} kg", "+Good")
    col4.metric("Diversion Rate", f"{div_rate:.1f}%", f"{div_rate-50:.1f}% vs Target")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Waste Composition")
        if grand_total > 0:
            fig, ax = plt.subplots()
            ax.pie([total_recycling, total_compost, total_landfill], 
                   labels=['Recycling', 'Compost', 'Landfill'], 
                   autopct='%1.1f%%', colors=['#36A2EB', '#FFCE56', '#FF6384'])
            st.pyplot(fig)
        else:
            st.warning("No data yet.")

    with c2:
        st.subheader("Historical Trend")
        st.line_chart(df.set_index("Date"))

# === PAGE 2: LOGGER ===
elif menu == "📝 Daily Logger":
    st.title("📝 Data Entry Portal")
    with st.form("waste_form"):
        col1, col2, col3 = st.columns(3)
        r = col1.number_input("Recycling (kg)", 0.0, 1000.0, 10.0)
        c = col2.number_input("Compost (kg)", 0.0, 1000.0, 5.0)
        l = col3.number_input("Landfill (kg)", 0.0, 1000.0, 20.0)
        submitted = st.form_submit_button("💾 Save to Database")
        if submitted:
            save_entry(r, c, l)
            st.success("Entry saved!")

    st.subheader("Recent Entries")
    st.dataframe(df.tail(5))

# === PAGE 3: SMART SORTER ===
elif menu == "🔍 Smart Sorter":
    st.title("🔍 Smart Waste Sorter")
    search_term = st.text_input("Enter item name (e.g., 'Pizza Box', 'Battery'):")
    if search_term:
        result = get_waste_advice(search_term)
        st.info(f"**Result:** {result}")

# === PAGE 4: AI ANALYST ===
elif menu == "🔮 AI Analyst":
    st.title("🔮 AI Predictive Analytics")
    df['Week_Num'] = range(1, len(df) + 1)
    df['Rate'] = ((df['Recycling'] + df['Compost']) / (df['Recycling'] + df['Compost'] + df['Landfill'])) * 100
    
    if len(df) > 1:
        model = LinearRegression()
        X = df[['Week_Num']]
        y = df['Rate'].fillna(0)
        model.fit(X, y)
        future_weeks = np.array(range(len(df)+1, len(df)+5)).reshape(-1, 1)
        predictions = model.predict(future_weeks)
        
        fig, ax = plt.subplots()
        ax.plot(df['Week_Num'], df['Rate'], 'o-', label='Historical Actuals')
        ax.plot(future_weeks, predictions, 'x--', color='red', label='AI Forecast')
        ax.set_ylabel("Diversion Rate (%)")
        ax.legend()
        st.pyplot(fig)
        st.success(f"Predicted Rate Next Week: **{predictions[0]:.1f}%**")
    else:
        st.error("Need more data to predict.")

# === PAGE 5: GAMIFICATION ===
elif menu == "🏆 Gamification":
    st.title("🏆 Eco-Warrior Profile")
    total_saved = df['Recycling'].sum() + df['Compost'].sum()
    level = int(total_saved // 100) + 1 
    
    col1, col2 = st.columns([1, 2])
    with col1:
        # REPLACED IMAGE WITH EMOJI HERE
        st.markdown("# 🌍")
    with col2:
        st.header(f"Rank: Level {level}")
        st.metric("Total Diverted", f"{total_saved:.1f} kg")
        st.progress((total_saved % 100) / 100)
    st.subheader("🏅 Badges Earned")
    badges = []
    if total_saved > 10: badges.append("🌱 The Beginner (Saved 10kg)")
    if total_saved > 100: badges.append("🌿 The Recycler (Saved 100kg)")
    if total_saved > 500: badges.append("🌳 The Guardian (Saved 500kg)")
    
    if badges:
        for b in badges:
            st.success(b)
    else:
        st.write("Start logging waste to earn badges!")