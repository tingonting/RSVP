import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================
# CONFIG — edit these three lines to personalize the page
# ============================================================
COUPLE_NAMES = "The Happy Couple"     # e.g. "Alex & Jamie"
WEDDING_DATE = "Your Wedding Date"    # e.g. "October 17th, 2026"
VENUE = ""                            # e.g. "The Orchard House, Worcestershire" (leave blank to hide)
HOST_PASSWORD = "wedding2026"         # change this before sharing the link
# ============================================================

st.set_page_config(
    page_title=f"{COUPLE_NAMES} — RSVP",
    page_icon="🌸",
    layout="centered"
)

# --- BLUSH & IVORY STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,500&family=Jost:wght@300;400;500;600&display=swap');

    :root {
        --ivory: #FBF7F4;
        --ink: #3A2E2E;
        --blush: #EFD9D9;
        --rose: #B76E79;
        --rose-deep: #9C5560;
        --gold: #C9A66B;
        --sage: #8FA379;
        --card-shadow: rgba(183, 110, 121, 0.14);
    }

    .stApp {
        background-color: var(--ivory);
        color: var(--ink);
        font-family: 'Jost', sans-serif;
    }

    #MainMenu, footer, header {visibility: hidden;}

    h1, h2, h3 {
        font-family: 'Cormorant Garamond', serif;
        color: var(--ink);
        letter-spacing: 0.02em;
    }

    .hero-eyebrow {
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 0.35em;
        font-size: 0.7rem;
        color: var(--rose-deep);
        font-weight: 500;
        margin-bottom: 0.4rem;
    }

    .hero-names {
        text-align: center;
        font-family: 'Cormorant Garamond', serif;
        font-weight: 500;
        font-size: 3.1rem;
        line-height: 1.1;
        color: var(--ink);
        margin: 0;
    }

    .hero-names em {
        color: var(--rose);
        font-style: italic;
    }

    .hero-date {
        text-align: center;
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.35rem;
        color: var(--rose-deep);
        margin-top: 0.3rem;
    }

    .hero-venue {
        text-align: center;
        font-size: 0.85rem;
        color: #8A7B7B;
        letter-spacing: 0.08em;
        margin-top: 0.2rem;
    }

    .sprig-divider {
        display: flex;
        justify-content: center;
        margin: 1.6rem 0;
    }

    .section-label {
        text-transform: uppercase;
        letter-spacing: 0.28em;
        font-size: 0.72rem;
        color: var(--rose-deep);
        font-weight: 500;
        text-align: center;
        margin-bottom: 0.3rem;
    }

    .section-sub {
        text-align: center;
        color: #8A7B7B;
        font-size: 0.95rem;
        margin-bottom: 1.6rem;
    }

    div[data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 2.4rem 2.2rem;
        border-radius: 6px;
        box-shadow: 0 12px 32px var(--card-shadow);
        border: 1px solid var(--blush);
        position: relative;
    }

    div[data-testid="stForm"]::before {
        content: "";
        position: absolute;
        top: 10px; left: 10px; right: 10px; bottom: 10px;
        border: 1px solid var(--blush);
        border-radius: 3px;
        pointer-events: none;
    }

    .stTextInput input, .stTextArea textarea {
        border-radius: 4px !important;
        border: 1px solid #E4D3D3 !important;
        background-color: #FEFCFB !important;
        font-family: 'Jost', sans-serif !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--rose) !important;
        box-shadow: 0 0 0 1px var(--rose) !important;
    }

    label p {
        font-family: 'Jost', sans-serif !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.04em;
        color: var(--ink) !important;
        text-transform: uppercase;
    }

    .guest-tag {
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        font-size: 1.15rem;
        color: var(--rose-deep);
        margin-bottom: 0.4rem;
        margin-top: 0.6rem;
    }

    .stButton>button, .stFormSubmitButton>button {
        border-radius: 30px !important;
        font-family: 'Jost', sans-serif !important;
        font-weight: 500 !important;
        letter-spacing: 0.05em;
        padding: 0.6rem 1rem !important;
        border: 1px solid var(--rose) !important;
        transition: all 0.2s ease;
    }

    div[data-testid="stForm"] button[kind="secondaryFormSubmit"]:nth-of-type(1),
    .stFormSubmitButton>button {
        background-color: var(--rose) !important;
        color: #FFFFFF !important;
    }

    .stFormSubmitButton>button:hover {
        background-color: var(--rose-deep) !important;
        border-color: var(--rose-deep) !important;
    }

    .footer-note {
        text-align: center;
        font-family: 'Cormorant Garamond', serif;
        font-style: italic;
        color: #A99B9B;
        font-size: 0.95rem;
        margin-top: 2.2rem;
    }
    </style>
""", unsafe_allow_html=True)

SPRIG_SVG = """
<div class="sprig-divider">
<svg width="180" height="28" viewBox="0 0 180 28" fill="none" xmlns="http://www.w3.org/2000/svg">
  <line x1="0" y1="14" x2="70" y2="14" stroke="#C9A66B" stroke-width="1"/>
  <line x1="110" y1="14" x2="180" y2="14" stroke="#C9A66B" stroke-width="1"/>
  <path d="M90 14 C86 8, 78 8, 76 14 C78 20, 86 20, 90 14 Z" fill="#EFD9D9" stroke="#B76E79" stroke-width="0.8"/>
  <path d="M90 14 C94 8, 102 8, 104 14 C102 20, 94 20, 90 14 Z" fill="#EFD9D9" stroke="#B76E79" stroke-width="0.8"/>
  <circle cx="90" cy="14" r="2.4" fill="#C9A66B"/>
  <path d="M76 14 C72 12, 70 14, 70 16" stroke="#8FA379" stroke-width="1" fill="none"/>
  <path d="M104 14 C108 12, 110 14, 110 16" stroke="#8FA379" stroke-width="1" fill="none"/>
</svg>
</div>
"""

# --- INITIALIZE SESSION STATE ---
if 'rsvp_data' not in st.session_state:
    st.session_state['rsvp_data'] = []

# --- HERO ---
st.markdown("<div class='hero-eyebrow'>Together with our families</div>", unsafe_allow_html=True)
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
st.markdown("<div class='section-label'>Kindly Respond</div>", unsafe_allow_html=True)
st.markdown("<div class='section-sub'>We would love to celebrate with you — please let us know by the date on your invitation.</div>", unsafe_allow_html=True)

with st.form("rsvp_form"):
    st.markdown("<div class='guest-tag'>Guest One</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        g1_first = st.text_input("First Name", key="g1_first")
    with col2:
        g1_last = st.text_input("Surname", key="g1_last")

    st.markdown("<div class='guest-tag'>Guest Two · optional</div>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)
    with col3:
        g2_first = st.text_input("First Name", key="g2_first")
    with col4:
        g2_last = st.text_input("Surname", key="g2_last")

    notes = st.text_area("Dietary requirements or song requests · optional", height=80)

    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        attending_btn = st.form_submit_button("🥂 Joyfully Attending")
    with col_btn2:
        not_attending_btn = st.form_submit_button("Regretfully Decline")

    if attending_btn or not_attending_btn:
        status = "Attending" if attending_btn else "Not Attending"

        if not g1_first or not g1_last:
            st.error("Please provide at least Guest 1's first name and surname.")
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

    if host_password == HOST_PASSWORD:
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
