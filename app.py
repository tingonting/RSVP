import streamlit as st
import pandas as pd
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Our Wedding RSVP",
    page_icon="💍",
    layout="centered"
)

# --- WEDDING VIBE STYLING (CSS) ---
st.markdown("""
    <style>
    /* Main background and font styling */
    .stApp {
        background-color: #FDFBF7;
        color: #4A4A4A;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #7A5C58;
        font-family: serif;
    }
    
    /* Buttons styling */
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
        padding: 10px 20px;
        border: none;
    }
    
    /* Custom container for a card look */
    .rsvp-card {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(122, 92, 88, 0.1);
        border: 1px solid #F0E6E1;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE FOR DATA STORAGE ---
if 'rsvp_data' not in st.session_state:
    st.session_state['rsvp_data'] = []

# --- APP HEADER ---
st.markdown("<h1 style='text-align: center;'>Save the Date</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #9E7B77;'>November 7th, 2026</h3>", unsafe_allow_html=True)
st.write("---")

# --- MAIN RSVP FORM ---
with st.container():
    st.markdown("### Please Respond")
    st.write("We would love to celebrate with you. Please let us know if you can make it!")

    with st.form("rsvp_form"):
        # Guest 1 Section
        st.markdown("**Guest 1 (Primary)**")
        col1, col2 = st.columns(2)
        with col1:
            g1_first = st.text_input("First Name (Guest 1)")
        with col2:
            g1_last = st.text_input("Surname (Guest 1)")

        st.markdown("")

        # Guest 2 Section (Optional)
        st.markdown("**Guest 2 (Optional / Partner)**")
        col3, col4 = st.columns(2)
        with col3:
            g2_first = st.text_input("First Name (Guest 2)")
        with col4:
            g2_last = st.text_input("Surname (Guest 2)")

        st.write("---")
        
        # Action Buttons
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            attending_btn = st.form_submit_button("🥂 Joyfully Attending")
        with col_btn2:
            not_attending_btn = st.form_submit_button(" Regretfully Decline")

        if attending_btn or not_attending_btn:
            status = "Attending" if attending_btn else "Not Attending"
            
            if not g1_first or not g1_last:
                st.error("Please provide at least Guest 1's First and Surname.")
            else:
                # Save the entry
                new_entry = {
                    "Guest 1": f"{g1_first} {g1_last}",
                    "Guest 2": f"{g2_first} {g2_last}" if g2_first and g2_last else "None",
                    "Status": status,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state['rsvp_data'].append(new_entry)
                
                if status == "Attending":
                    st.success(f"Thank you, {g1_first}! We have recorded your attendance. Can't wait to celebrate!")
                else:
                    st.info(f"Thank you for letting us know, {g1_first}. You will be missed!")

# --- HOST LOGIN SECTION ---
st.write("---")
with st.expander("🔐 Host Login"):
    host_password = st.text_input("Enter Host Password", type="password")
    
    # Simple default password for now: 'wedding2026'
    if host_password == "wedding2026":
        st.success("Access Granted")
        st.markdown("### RSVP Responses Dashboard")
        
        if len(st.session_state['rsvp_data']) > 0:
            df = pd.DataFrame(st.session_state['rsvp_data'])
            st.dataframe(df, use_container_width=True)
            
            # Summary metrics
            total_responses = len(df)
            attending_count = len(df[df['Status'] == 'Attending'])
            st.metric(label="Total Responses", value=total_responses)
            st.metric(label="Total Attending", value=attending_count)
        else:
            st.write("No RSVPs submitted yet.")
    elif host_password:
        st.error("Incorrect password.")