import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================
# CONFIG — edit these lines to personalize the page
# ============================================================
COUPLE_NAMES = "Josie & Conor"                                   # e.g. "Alex & Jamie"
WEDDING_DATE = "7th November 2026"                                # e.g. "October 17th, 2026"
VENUE = "Ansty Golf Centre, Brinklow Rd, Coventry CV7 9JL"        # e.g. "The Orchard House, Worcestershire" (leave blank to hide)
# Host password now lives in Streamlit secrets — see .streamlit/secrets.toml
# ============================================================

st.set_page_config(
    page_title=f"{COUPLE_NAMES} — RSVP",
    page_icon="🌸",
    layout="centered"
)

# --- SAGE & TERRACOTTA STYLING (large text, high contrast, responsive) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500;1,9..144,600&family=Work+Sans:wght@300;400;500;600&display=swap');

    :root {
        --ivory: #F2EEE0;
        --card: #FBF8EE;
        --ink: #423B2E;
        --border: #DED2B8;
        --terracotta: #B9622F;
        --terracotta-deep: #93491F;
        --sage: #7C8B6F;
        --sage-light: #9CAF88;
        --card-shadow: rgba(140, 110, 70, 0.14);
    }

    html, body, .stApp {
        background-color: var(--ivory);
        color: var(--ink);
        font-family: 'Work Sans', sans-serif;
        font-size: 18px;
    }

    #MainMenu, footer, header {visibility: hidden;}

    .block-container {
        max-width: 720px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Fraunces', serif;
        color: var(--ink);
    }

    .hero-eyebrow {
        text-align: center;
        letter-spacing: 0.03em;
        font-size: clamp(1rem, 2.4vw, 1.15rem);
        color: var(--terracotta);
        font-weight: 500;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }

    .hero-names {
        text-align: center;
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-style: italic;
        font-size: clamp(2.4rem, 8vw, 3.4rem);
        line-height: 1.15;
        color: var(--ink);
        margin: 0;
    }

    .hero-names em {
        color: var(--terracotta);
        font-style: italic;
    }

    .hero-date {
        text-align: center;
        color: var(--sage);
        font-weight: 500;
        font-size: clamp(1.2rem, 3.5vw, 1.4rem);
        margin-top: 0.4rem;
    }

    .hero-venue {
        text-align: center;
        font-size: clamp(0.9rem, 2.2vw, 1rem);
        color: #8A7F6A;
        margin-top: 0.3rem;
    }

    .sprig-divider {
        display: flex;
        justify-content: center;
        margin: 1.8rem 0;
    }

    .section-label {
        font-size: clamp(1.3rem, 3.5vw, 1.6rem);
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-weight: 600;
        color: var(--terracotta);
        text-align: center;
        margin-bottom: 0.4rem;
    }

    .section-sub {
        text-align: center;
        color: #6E6252;
        font-size: clamp(1rem, 2.5vw, 1.1rem);
        margin-bottom: 1.8rem;
        line-height: 1.5;
    }

    div[data-testid="stForm"] {
        background-color: var(--card);
        padding: clamp(1.4rem, 5vw, 2.6rem);
        border-radius: 18px;
        box-shadow: 0 12px 32px var(--card-shadow);
        border: none;
    }

    .stTextInput input, .stTextArea textarea {
        border-radius: 6px !important;
        border: 1.5px solid var(--border) !important;
        background-color: #FEFDF8 !important;
        font-family: 'Work Sans', sans-serif !important;
        font-size: 1.1rem !important;
        padding: 0.7rem 0.8rem !important;
        color: var(--ink) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--terracotta) !important;
        box-shadow: 0 0 0 2px #EFE1CC !important;
    }

    label p, .stRadio label p {
        font-family: 'Work Sans', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 500;
        color: var(--ink) !important;
    }

    .guest-tag {
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-weight: 600;
        font-size: 1.4rem;
        color: var(--sage);
        margin-bottom: 0.5rem;
        margin-top: 0.8rem;
    }

    div[role="radiogroup"] {
        gap: 0.6rem;
    }

    div[role="radiogroup"] label {
        border: 1.5px solid var(--border);
        border-radius: 8px;
        padding: 0.7rem 1rem !important;
        background-color: #FEFDF8;
    }

    div[role="radiogroup"] label p {
        font-size: 1.15rem !important;
    }

    .stButton>button, .stFormSubmitButton>button {
        border-radius: 30px !important;
        font-family: 'Work Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
        padding: 0.85rem 1.5rem !important;
        border: 1.5px solid var(--border) !important;
        color: var(--sage) !important;
        width: 100%;
        transition: all 0.2s ease;
    }

    .stFormSubmitButton>button {
        background-color: var(--terracotta) !important;
        border: 1.5px solid var(--terracotta) !important;
        color: #FBF8EE !important;
    }

    .stFormSubmitButton>button:hover {
        background-color: var(--terracotta-deep) !important;
        border-color: var(--terracotta-deep) !important;
    }

    /* Second RSVP button (Decline) reads as secondary/outlined */
    div[data-testid="column"]:nth-of-type(2) .stFormSubmitButton>button {
        background-color: transparent !important;
        border: 1.5px solid var(--border) !important;
        color: var(--sage) !important;
    }

    div[data-testid="column"]:nth-of-type(2) .stFormSubmitButton>button:hover {
        background-color: #F3EEDD !important;
        border-color: var(--sage) !important;
    }

    .footer-note {
        text-align: center;
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 1.15rem;
        color: #A6987F;
        margin-top: 2.4rem;
    }

    /* Extra breathing room on larger screens */
    @media (min-width: 900px) {
        .block-container { padding-top: 3.5rem; }
    }

    /* Tighten up on small phones */
    @media (max-width: 480px) {
        html, body, .stApp { font-size: 17px; }
        div[data-testid="stForm"] { padding: 1.2rem; }
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column;
        }
        div[data-testid="stHorizontalBlock"] > div {
            width: 100% !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

SPRIG_SVG = """
<div class="sprig-divider">
<svg width="150" height="26" viewBox="0 0 150 26" fill="none" xmlns="http://www.w3.org/2000/svg">
  <line x1="10" y1="13" x2="140" y2="13" stroke="#DED2B8" stroke-width="1"/>
  <circle cx="50" cy="13" r="4" fill="#9CAF88"/>
  <circle cx="65" cy="9" r="3" fill="#DED2B8"/>
  <circle cx="75" cy="13" r="4.5" fill="#B9622F"/>
  <circle cx="88" cy="9" r="3" fill="#DED2B8"/>
  <circle cx="100" cy="13" r="4" fill="#9CAF88"/>
</svg>
</div>
"""

# --- INITIALIZE SESSION STATE ---
if 'rsvp_data' not in st.session_state:
    st.session_state['rsvp_data'] = []

# --- HERO ---
st.markdown("<div class='hero-eyebrow'>You are invited to celebrate the wedding of</div>", unsafe_allow_html=True)
if "&" in COUPLE_NAMES:
    display_names = COUPLE_NAMES.replace("&", "<em>&</em>")
else:
    display_names = COUPLE_NAMES
st.markdown(f"<h1 class='hero-names'>{display_names}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='hero-date'>{WEDDING_DATE}</div>", unsafe_allow_html=True)
if VENUE:
    st.markdown(f"<div class='hero-venue'>{VENUE.upper()}</div>", unsafe_allow_html=True)
st.markdown(SPRIG_SVG, unsafe_allow_html=True)

# --- RSVP FORM ---
st.markdown("<div class='section-label'>Please Let Us Know</div>", unsafe_allow_html=True)
st.markdown("<div class='section-sub'>Fill in your name below and let us know if you can join us.</div>", unsafe_allow_html=True)

with st.form("rsvp_form"):
    st.markdown("<div class='guest-tag'>Your Name</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        g1_first = st.text_input("First Name", key="g1_first")
    with col2:
        g1_last = st.text_input("Last Name", key="g1_last")

    st.markdown("<div class='guest-tag'>Bringing a Guest? (optional)</div>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        g2_first = st.text_input("First Name ", key="g2_first")
    with col4:
        g2_last = st.text_input("Last Name ", key="g2_last")

    notes = st.text_area(
        "Dietary requirements or song requests (optional)",
        height=80
    )

    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        attending_btn = st.form_submit_button("🥂 Joyfully Attending")
    with col_btn2:
        not_attending_btn = st.form_submit_button("Regretfully Decline")

    if attending_btn or not_attending_btn:
        status = "Attending" if attending_btn else "Not Attending"

        if not g1_first or not g1_last:
            st.error("Please enter your first and last name above.")
        else:
            new_entry = {
                "Guest 1": f"{g1_first} {g1_last}",
                "Guest 2": f"{g2_first} {g2_last}" if g2_first and g2_last else "None",
                "Status": status,
                "Notes": notes if notes else "—",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state['rsvp_data'].append(new_entry)

            if status == "Attending":
                st.success(f"Thank you, {g1_first} — we can't wait to celebrate with you! 🌸")
            else:
                st.info(f"Thank you for letting us know, {g1_first}. You'll be missed.")

st.markdown("<div class='footer-note'>With love, looking forward to seeing you there</div>", unsafe_allow_html=True)

# --- HOST LOGIN SECTION ---
st.write("")
st.write("")
with st.expander("🔐 Host Login"):
    host_password = st.text_input("Enter Host Password", type="password")

    if "host_password" not in st.secrets:
        st.error("No host password is set. Add one to `.streamlit/secrets.toml` (see below).")
    elif host_password == st.secrets["host_password"]:
        st.success("Access Granted")
        st.markdown("### RSVP Responses Dashboard")

        if len(st.session_state['rsvp_data']) > 0:
            df = pd.DataFrame(st.session_state['rsvp_data'])
            st.dataframe(df, use_container_width=True)

            total_responses = len(df)
            guest_counts = df['Guest 2'].apply(lambda g: 2 if g and g != "None" else 1)
            attending_guest_count = int(guest_counts[df['Status'] == 'Attending'].sum())
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(label="Total Responses", value=total_responses)
            with col_m2:
                st.metric(label="Total Attending", value=attending_guest_count)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download responses as CSV", csv, "rsvp_responses.csv", "text/csv")

            st.write("---")
            st.markdown("#### Remove an Entry")

            entry_labels = [
                f"{i} — {row['Guest 1']} ({row['Status']})"
                for i, row in enumerate(st.session_state['rsvp_data'])
            ]
            selected_label = st.selectbox("Select an entry to remove", entry_labels, key="delete_select")
            selected_index = entry_labels.index(selected_label)

            if 'pending_delete' not in st.session_state:
                st.session_state['pending_delete'] = None

            # If a different entry is picked after a pending confirmation, reset it
            if st.session_state['pending_delete'] is not None and st.session_state['pending_delete'] != selected_index:
                st.session_state['pending_delete'] = None

            if st.session_state['pending_delete'] is None:
                if st.button("🗑️ Remove Entry", key="delete_request"):
                    st.session_state['pending_delete'] = selected_index
                    st.rerun()
            else:
                target = st.session_state['rsvp_data'][st.session_state['pending_delete']]
                st.warning(f"Remove **{target['Guest 1']}**'s RSVP? This can't be undone.")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("✅ Yes, remove it", key="delete_confirm"):
                        st.session_state['rsvp_data'].pop(st.session_state['pending_delete'])
                        st.session_state['pending_delete'] = None
                        st.success("Entry removed.")
                        st.rerun()
                with col_c2:
                    if st.button("Cancel", key="delete_cancel"):
                        st.session_state['pending_delete'] = None
                        st.rerun()
        else:
            st.write("No RSVPs submitted yet.")
    elif host_password:
        st.error("Incorrect password.")
