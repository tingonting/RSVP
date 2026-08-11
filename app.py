import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- FILE CONFIGURATION ---
DATA_FILE = "rsvp_data.xlsx"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Guest 1", "Guest 2", "Status", "Headcount", "Timestamp"])

def save_data(new_row):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(DATA_FILE, index=False)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Josie & Conor's Wedding RSVP",
    page_icon="💍",
    layout="centered"
)

# --- STYLING (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #FAF7F5; font-family: 'Plus Jakarta Sans', sans-serif; }
    h1, h2, h3, h4 { font-family: 'Playfair Display', serif; color: #4A3B32; }
    .hero-container {
        background: linear-gradient(135deg, #F4ECE6 0%, #EADCD3 100%);
        padding: 40px 20px; border-radius: 16px; text-align: center; margin-bottom: 30px;
    }
    .hero-title { font-size: 2.2rem; color: #4A3B32; font-weight: 600; }
    div[data-testid="stForm"] { background-color: #FFFFFF; padding: 35px; border-radius: 20px; }
    .stFormSubmitButton > button:first-child { background-color: #5A6B5C !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- HERO HEADER ---
st.markdown("""
    <div class="hero-container">
        <p>You Are Invited</p>
        <h1 class="hero-title">To celebrate the wedding of<br>Josie & Conor</h1>
        <hr style="width: 60px; border: none; height: 1px; background-color: #C5B2A5; margin: 15px auto;">
        <p style="font-style: italic;">November 7th, 2026</p>
    </div>
""", unsafe_allow_html=True)

# --- RSVP FORM ---
with st.form("rsvp_form"):
    st.markdown("### Kindly Respond")
    col1, col2 = st.columns(2)
    g1_first = st.text_input("First Name (Guest 1)")
    g1_last = st.text_input("Surname (Guest 1)")
    col3, col4 = st.columns(2)
    g2_first = st.text_input("First Name (Guest 2)")
    g2_last = st.text_input("Surname (Guest 2)")
    
    col_btn1, col_btn2 = st.columns(2)
    attending_btn = col_btn1.form_submit_button("🥂 Joyfully Attending")
    not_attending_btn = col_btn2.form_submit_button("🕊️ Regretfully Decline")

    if attending_btn or not_attending_btn:
        status = "Attending" if attending_btn else "Not Attending"
        if not g1_first or not g1_last:
            st.error("Please provide Guest 1's Name.")
        else:
            has_guest_2 = bool(g2_first and g2_last)
            row = {
                "Guest 1": f"{g1_first} {g1_last}",
                "Guest 2": f"{g2_first} {g2_last}" if has_guest_2 else "None",
                "Status": status,
                "Headcount": 2 if (status == "Attending" and has_guest_2) else (1 if status == "Attending" else 0),
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_data(row)
            st.success("Response saved!")

# --- HOST LOGIN ---
with st.expander("🔐 Host Login"):
    if st.text_input("Enter Password", type="password") == "wedding2026":
        df = load_data()
        st.dataframe(df, use_container_width=True)
        st.metric("Total Guests Attending", df['Headcount'].sum())
