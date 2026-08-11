import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Our Wedding RSVP",
    page_icon="💍",
    layout="centered"
)

# --- ENHANCED WEDDING VIBE STYLING (CSS) ---
st.markdown("""
    <style>
    /* Import Google Fonts for a romantic wedding aesthetic */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Plus+Jakarta+Sans:wght@300;400;500&display=swap');

    /* Global App Styles */
    .stApp {
        background-color: #FAF7F5;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #2C2C2C;
    }
    
    /* Typography */
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif;
        color: #4A3B32;
    }

    /* Hero Invitation Banner */
    .hero-container {
        background: linear-gradient(135deg, #F4ECE6 0%, #EADCD3 100%);
        padding: 40px 20px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(74, 59, 50, 0.05);
        border: 1px solid #E3D2C5;
    }
    
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        color: #4A3B32;
        margin-bottom: 5px;
        font-weight: 600;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        color: #8C7365;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 0px;
    }

    /* Form Container Card */
    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(74, 59, 50, 0.06);
        border: 1px solid #EFE6E1;
    }

    /* Text Inputs */
    .stTextInput input {
        background-color: #FCFBF9;
        border: 1px solid #E6DCD5;
        border-radius: 10px;
        color: #4A3B32;
        padding: 10px;
    }
    
    .stTextInput input:focus {
        border-color: #B89789;
        box-shadow: 0 0 0 1px #B89789;
    }

    /* Buttons Styling */
    .stFormSubmitButton > button {
        width: 100%;
        border-radius: 30px;
        font-weight: 500;
        padding: 12px 20px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        transition: all 0.3s ease;
    }
    
    /* Make Attending button stand out elegantly */
    .stFormSubmitButton > button:first-child {
        background-color: #5A6B5C !important;
        color: white !important;
        border: none;
    }
    
    .stFormSubmitButton > button:hover {
        opacity: 0.9;
        transform: translateY(-2px);
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'rsvp_data' not in st.session_state:
    st.session_state['rsvp_data'] = []

# --- HERO INVITATION HEADER ---
st.markdown("""
    <div class="hero-container">
        <p class="hero-subtitle">The Wedding Of</p>
        <h1 class="hero-title">You Are Invited</h1>
        <hr style="width: 60px; border: none; height: 1px; background-color: #C5B2A5; margin: 15px auto;">
        <p style="font-size: 1.2rem; color: #6E574B; font-family: 'Playfair Display', serif; font-style: italic;">
            November 7th, 2026
        </p>
    </div>
""", unsafe_allow_html=True)

# --- MAIN RSVP FORM ---
with st.form("rsvp_form"):
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>Kindly Respond</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #736257; margin-bottom: 30px;'>Please let us know if you'll be able to join our celebration.</p>", unsafe_allow_html=True)

    # Guest 1 Section
    st.markdown("<h4 style='font-size: 1.1rem; color: #5C4A3F;'>✨ Guest 1 (Primary)</h4>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        g1_first = st.text_input("First Name", key="g1_f")
    with col2:
        g1_last = st.text_input("Surname", key="g1_l")

    st.markdown("<div style='margin: 20px 0;'></div>", unsafe_allow_html=True)

    # Guest 2 Section (Optional)
    st.markdown("<h4 style='font-size: 1.1rem; color: #5C4A3F;'>✨ Guest 2 (Optional / Partner)</h4>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        g2_first = st.text_input("First Name", key="g2_f")
    with col4:
        g2_last = st.text_input("Surname", key="g2_l")

    st.markdown("<div style='margin: 30px 0; border-top: 1px solid #EFE6E1;'></div>", unsafe_allow_html=True)
    
    # Action Buttons Layout
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        attending_btn = st.form_submit_button("🥂 Joyfully Attending")
    with col_btn2:
        not_attending_btn = st.form_submit_button("🕊️ Regretfully Decline")

    if attending_btn or not_attending_btn:
        status = "Attending" if attending_btn else "Not Attending"
        
        if not g1_first or not g1_last:
            st.error("Please provide at least Guest 1's First Name and Surname.")
        else:
            new_entry = {
                "Guest 1": f"{g1_first} {g1_last}",
                "Guest 2": f"{g2_first} {g2_last}" if g2_first and g2_last else "None",
                "Status": status,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state['rsvp_data'].append(new_entry)
            
            if status == "Attending":
                st.success(f"Thank you, {g1_first}! Your response has been saved. We can't wait to celebrate with you!")
            else:
                st.info(f"Thank you for letting us know, {g1_first}. You will certainly be missed!")

# --- HOST LOGIN SECTION ---
st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)
with st.expander("🔐 Host Login"):
    host_password = st.text_input("Enter Host Password", type="password")
    
    if host_password == "wedding2026":
        st.success("Access Granted")
        st.markdown("### RSVP Responses Dashboard")
        
        if len(st.session_state['rsvp_data']) > 0:
            df = pd.DataFrame(st.session_state['rsvp_data'])
            st.dataframe(df, use_container_width=True)
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(label="Total Responses", value=len(df))
            with col_m2:
                st.metric(label="Total Attending", value=len(df[df['Status'] == 'Attending']))
        else:
            st.write("No RSVPs submitted yet.")
    elif host_password:
        st.error("Incorrect password.")
