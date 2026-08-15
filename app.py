import streamlit as st
import pandas as pd
import os
import uuid
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from urllib.parse import quote

# ============================================================
# CONFIG — edit these lines to personalize the page
# ============================================================
COUPLE_NAMES = "Josie & Conor"                                     # e.g. "Alex & Jamie"
WEDDING_DATE = "7th November 2026"                                  # display text, e.g. "October 17th, 2026"
VENUE = "Ansty Golf Centre, Brinklow Rd, Coventry CV7 9JL"          # leave blank to hide
TIMINGS = "4:00pm start · Last orders 11:00pm · Carriages 11:30pm"  # leave blank to hide
DRESS_CODE = "Smart Casual"                                         # leave blank to hide

GOOGLE_SHEET_NAME = "rsvp_data"   # must match the exact name of your Google Sheet

# Nearby hotels for guests staying over — edit/add/remove entries as needed.
HOTELS = [
    {
        "name": "Sparrow Hotel",
        "address": "Combe Fields Rd, Coventry CV7 9JP",
        "distance": "1.2 miles",
        "drive_time": "3 min drive",
        "website": "https://www.sparrowhotel.co.uk/",
        "notes": "",
    },
    {
        "name": "DoubleTree by Hilton Coventry",
        "address": "Paradise Way, Walsgrave on Sowe, Coventry CV2 2ST",
        "distance": "2.3 miles",
        "drive_time": "8 min drive",
        "website": "https://www.hilton.com/en/hotels/cvthndi-doubletree-coventry/",
        "notes": "",
    },
    {
        "name": "Premier Inn Coventry East",
        "address": "Gielgud Wy, Coventry CV2 2SZ",
        "distance": "2.3 miles",
        "drive_time": "7 min drive",
        "website": "https://www.premierinn.com/gb/en/hotels/england/west-midlands/coventry/coventry-east-m6jct2.html",
        "notes": "",
    },
    {
        "name": "Holiday Inn Coventry M6, Jct.2",
        "address": "Hinckley Rd, Coventry CV2 2HP",
        "distance": "2.1 miles",
        "drive_time": "7 min drive",
        "website": "https://www.ihg.com/holidayinn/hotels/gb/en/coventry/cvthr/hoteldetail",
        "notes": "",
    },
]

# Used to build the "Add to Calendar" file — keep in sync with WEDDING_DATE/TIMINGS above
EVENT_START = datetime(2026, 11, 7, 16, 0)   # 4:00pm
EVENT_END = datetime(2026, 11, 7, 23, 30)    # 11:30pm carriages

# Host password now lives in Streamlit secrets — see .streamlit/secrets.toml
# ============================================================

DATA_COLUMNS = ["Guest 1", "Additional Guests", "Party Size", "Status", "Notes", "Timestamp"]

HERO_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "images", "IMG_0033.jpeg")


def get_base64_image(path):
    """Reads a local image and returns it as a base64 data URI, or None if missing."""
    if not os.path.exists(path):
        return None
    import base64
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    mime = "jpeg" if ext == "jpg" else ext
    return f"data:image/{mime};base64,{encoded}"


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

st.set_page_config(
    page_title=f"{COUPLE_NAMES} — RSVP",
    page_icon="🌸",
    layout="centered"
)

# --- SAGE & TERRACOTTA STYLING (large text, high contrast, responsive) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500;1,9..144,600&family=Great+Vibes&family=Work+Sans:wght@300;400;500;600&display=swap');

    :root {
        --ivory: #FDF1EC;
        --card: #FFF9F5;
        --ink: #4A3630;
        --border: #F3D4C4;
        --terracotta: #E8674A;
        --terracotta-deep: #C94F35;
        --sage: #C99A4A;
        --sage-light: #E3C27A;
        --card-shadow: rgba(232, 150, 120, 0.18);
    }

    html, body, .stApp {
        background-color: var(--ivory);
        color: var(--ink);
        font-family: 'Work Sans', sans-serif;
        font-size: 18px;
    }

    #MainMenu, footer, header {visibility: hidden;}
    header {height: 0 !important; min-height: 0 !important;}
    div[data-testid="stHeader"] {
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        visibility: hidden;
    }
    div[data-testid="stAppViewContainer"],
    div[data-testid="stMain"],
    section.stMain {
        padding-top: 0 !important;
    }

    .block-container {
        max-width: 720px;
        padding-top: 0 !important;
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

    .hero-time {
        text-align: center;
        font-size: clamp(0.9rem, 2.2vw, 1rem);
        color: #8A7F6A;
        margin-top: 0.2rem;
    }

    .hero-dresscode {
        text-align: center;
        font-size: clamp(0.9rem, 2.2vw, 1rem);
        color: #8A7F6A;
        margin-top: 0.2rem;
        font-style: italic;
    }

    .action-row {
        display: flex;
        gap: 12px;
        justify-content: center;
        margin-top: 1.4rem;
        flex-wrap: wrap;
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

    .rsvp-deadline {
        text-align: center;
        color: #B3261E;
        font-weight: 700;
        font-size: clamp(1rem, 2.5vw, 1.1rem);
        margin-top: -0.8rem;
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

    .hotel-card {
        background-color: var(--card);
        padding: clamp(1.1rem, 4vw, 1.6rem);
        border-radius: 16px;
        box-shadow: 0 8px 20px var(--card-shadow);
        margin-bottom: 1.1rem;
    }

    .hotel-name {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-style: italic;
        font-size: 1.35rem;
        color: var(--ink);
        margin-bottom: 0.3rem;
    }

    .hotel-address {
        color: #6E6252;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    .hotel-meta {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        color: var(--sage);
        font-weight: 500;
        font-size: 0.95rem;
        margin-bottom: 0.6rem;
    }

    .hotel-notes {
        color: #8A7F6A;
        font-size: 0.95rem;
        font-style: italic;
        margin-bottom: 0.6rem;
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

    /* Selectbox — anchored on data-testid, same approach that fixed the Host Login bar */
    div[data-testid="stSelectbox"] {
        background-color: transparent !important;
    }

    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border-radius: 6px !important;
        border: 1.5px solid var(--border) !important;
        background-color: #FEFDF8 !important;
        font-family: 'Work Sans', sans-serif !important;
        font-size: 1.1rem !important;
        min-height: 3rem;
    }

    div[data-testid="stSelectbox"] * {
        color: var(--ink) !important;
        background-color: transparent !important;
    }

    /* The dropdown arrow icon has an invisible hit-area shape inside it that
       was picking up our fill color and rendering as a solid block — simplest
       fix is to just hide the icon; the dropdown still opens fine on tap. */
    div[data-testid="stSelectbox"] svg {
        display: none !important;
    }

    /* The dropdown options list renders as a popover — force it light too */
    ul[data-baseweb="menu"], div[data-baseweb="popover"] {
        background-color: #FFFFFF !important;
    }

    li[data-baseweb="menu-item"], li[role="option"] {
        background-color: #FFFFFF !important;
        color: var(--ink) !important;
    }

    li[data-baseweb="menu-item"]:hover, li[role="option"]:hover,
    li[aria-selected="true"] {
        background-color: #F3EEDD !important;
        color: var(--ink) !important;
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

    .guest-subtag {
        font-family: 'Work Sans', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 0.04em;
        color: var(--terracotta);
        margin-bottom: 0.4rem;
        margin-top: 0.9rem;
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

    .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button, .stLinkButton>a {
        border-radius: 30px !important;
        font-family: 'Work Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        padding: 0.85rem 1.5rem !important;
        border: 1.5px solid var(--border) !important;
        color: var(--sage) !important;
        background-color: #FEFDF8 !important;
        transition: all 0.2s ease;
    }

    .stFormSubmitButton>button {
        width: 100%;
    }

    /* Primary action buttons (Joyfully Attending, Yes remove it) — solid terracotta.
       Targets Streamlit's own "kind" attribute rather than position, since column
       order/testids can change between Streamlit versions. Uses a substring match
       (*=) since form-submit buttons may render as "primary"/"primaryFormSubmit"
       or similar variants depending on Streamlit version. */
    button[kind*="primary"] {
        background-color: var(--terracotta) !important;
        border: 1.5px solid var(--terracotta) !important;
        color: #FBF8EE !important;
    }

    button[kind*="primary"]:hover {
        background-color: var(--terracotta-deep) !important;
        border-color: var(--terracotta-deep) !important;
    }

    /* Secondary/outlined buttons (Regretfully Decline, Cancel, etc.) */
    button[kind*="secondary"] {
        background-color: transparent !important;
        border: 1.5px solid var(--border) !important;
        color: var(--sage) !important;
    }

    button[kind*="secondary"]:hover {
        background-color: #F3EEDD !important;
        border-color: var(--sage) !important;
    }

    .stDownloadButton>button, .stLinkButton>a {
        text-decoration: none !important;
        text-align: center;
        display: inline-block;
        background-color: #FEFDF8 !important;
        border: 1.5px solid var(--border) !important;
        color: var(--sage) !important;
    }

    .stDownloadButton>button:hover, .stLinkButton>a:hover {
        background-color: #F3EEDD !important;
        border-color: var(--sage) !important;
    }

    /* Hotels nav button (top action row) — match the solid cream style of
       Add to Calendar / Get Directions rather than the outlined secondary
       style used for buttons like Cancel / Regretfully Decline. */
    .st-key-hotels_nav_btn button {
        background-color: #FEFDF8 !important;
        border: 1.5px solid var(--border) !important;
        color: var(--sage) !important;
    }

    .st-key-hotels_nav_btn button:hover {
        background-color: #F3EEDD !important;
        border-color: var(--sage) !important;
    }

    /* The password show/hide icon button inside the host login field */
    div[data-testid="stTextInput"] button,
    div[data-testid="stTextInputRootElement"] button {
        background-color: transparent !important;
        border: none !important;
    }

    div[data-testid="stTextInput"] button svg,
    div[data-testid="stTextInputRootElement"] button svg {
        fill: var(--ink) !important;
    }

    /* Host Login expander — force light styling on the header bar and body */
    div[data-testid="stExpander"] {
        border: 1.5px solid var(--border) !important;
        border-radius: 12px !important;
        background-color: var(--card) !important;
    }

    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] details {
        background-color: var(--card) !important;
        color: var(--ink) !important;
    }

    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span {
        color: var(--ink) !important;
    }

    div[data-testid="stExpander"] summary svg {
        fill: var(--terracotta) !important;
    }

    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        background-color: var(--card) !important;
    }

    /* Metrics inside the host dashboard (Total Responses / Total Attending) —
       force light styling so mobile dark-mode can't turn these white-on-white */
    div[data-testid="stMetric"] {
        background-color: var(--card) !important;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--ink) !important;
    }

    /* The responses dataframe — force light styling for the same reason */
    div[data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
    }

    .footer-note {
        text-align: center;
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 1.15rem;
        color: #A6987F;
        margin-top: 2.4rem;
    }

    /* Full-width rounded photo banner sitting above the hero names.
       Simple, in-flow layout — no cropping tricks, no absolute
       positioning — so it can't misbehave across browsers or clip
       guests out of frame. The bottom edge fades gently into the
       page instead of ending in a hard rectangle. */
    .hero-photo-banner {
        width: 100%;
        aspect-ratio: 4 / 3;
        border-radius: 28px;
        background-size: cover;
        background-position: center;
        box-shadow: 0 8px 22px rgba(140, 110, 70, 0.10);
        -webkit-mask-image: linear-gradient(to bottom, black 0%, black 78%, transparent 100%);
        mask-image: linear-gradient(to bottom, black 0%, black 78%, transparent 100%);
        margin-bottom: 1.4rem;
    }

    @media (max-width: 480px) {
        .hero-photo-banner {
            aspect-ratio: 1 / 1;
            border-radius: 22px;
            margin-bottom: 1.1rem;
        }
    }

    /* Note: block-container padding-top is intentionally 0 at every
       breakpoint so the corner photo sits flush against the very top
       with no gap, on both mobile and desktop. */

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


# --- PERSISTENT STORAGE HELPERS (Google Sheets) ---
@st.cache_resource
def get_worksheet():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1

    # Make sure the header row exists / matches, so a brand new sheet works too
    existing_headers = sheet.row_values(1)
    if existing_headers != DATA_COLUMNS:
        sheet.update("A1", [DATA_COLUMNS])

    return sheet


def load_rsvp_data():
    sheet = get_worksheet()
    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    if df.empty:
        return pd.DataFrame(columns=DATA_COLUMNS)

    for col in DATA_COLUMNS:
        if col not in df.columns:
            df[col] = None

    df["Party Size"] = pd.to_numeric(df["Party Size"], errors="coerce").fillna(1).astype("Int64")
    df["Additional Guests"] = df["Additional Guests"].replace("", "—").fillna("—")
    df["Notes"] = df["Notes"].replace("", "—").fillna("—")
    return df[DATA_COLUMNS]


def save_rsvp_data(df):
    sheet = get_worksheet()
    sheet.clear()
    values = [DATA_COLUMNS] + df[DATA_COLUMNS].astype(str).values.tolist()
    sheet.update("A1", values)


def build_ics():
    dt_fmt = "%Y%m%dT%H%M%S"
    stamp_fmt = "%Y%m%dT%H%M%SZ"
    return (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Wedding RSVP//EN\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{uuid.uuid4()}\r\n"
        f"DTSTAMP:{datetime.utcnow().strftime(stamp_fmt)}\r\n"
        f"DTSTART:{EVENT_START.strftime(dt_fmt)}\r\n"
        f"DTEND:{EVENT_END.strftime(dt_fmt)}\r\n"
        f"SUMMARY:{COUPLE_NAMES.replace('&', 'and')} Wedding\r\n"
        f"LOCATION:{VENUE}\r\n"
        f"DESCRIPTION:We can't wait to celebrate with you!\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )


# --- PAGE ROUTING (simple session-state toggle, no separate pages folder) ---
if "page" not in st.session_state:
    st.session_state["page"] = "home"


def go_to(page_name):
    st.session_state["page"] = page_name


if st.session_state["page"] == "hotels":
    if st.button("← Back to RSVP"):
        go_to("home")
        st.rerun()

    st.markdown("<div class='section-label'>Where to Stay</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-sub'>A few nearby options if you're staying over — "
        "distances and drive times are approximate from the venue.</div>",
        unsafe_allow_html=True
    )

    for hotel in HOTELS:
        st.markdown(f"<div class='hotel-name'>{hotel['name']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='hotel-address'>{hotel['address']}</div>", unsafe_allow_html=True)
        meta_bits = []
        if hotel.get("distance"):
            meta_bits.append(hotel["distance"])
        if hotel.get("drive_time"):
            meta_bits.append(hotel["drive_time"])
        if meta_bits:
            st.markdown(f"<div class='hotel-meta'>{' · '.join(meta_bits)}</div>", unsafe_allow_html=True)
        if hotel.get("notes"):
            st.markdown(f"<div class='hotel-notes'>{hotel['notes']}</div>", unsafe_allow_html=True)

        hotel_maps_url = f"https://www.google.com/maps/search/?api=1&query={quote(hotel['name'] + ', ' + hotel['address'])}"
        if hotel.get("website"):
            hcol1, hcol2 = st.columns(2)
            with hcol1:
                st.link_button("📍 Get Directions", hotel_maps_url, use_container_width=True)
            with hcol2:
                st.link_button("🌐 Website", hotel["website"], use_container_width=True)
        else:
            st.link_button("📍 Get Directions", hotel_maps_url, use_container_width=True)
        st.write("")

    st.stop()


# --- HERO PHOTO ---
hero_photo_uri = get_base64_image(HERO_IMAGE_PATH)
if hero_photo_uri:
    st.markdown(
        "<div class='hero-photo-banner' style=\""
        f"background-image: url('{hero_photo_uri}');"
        "width: 100%; aspect-ratio: 4 / 3; border-radius: 28px; "
        "background-size: cover; background-position: center; "
        "box-shadow: 0 8px 22px rgba(140, 110, 70, 0.10); "
        "-webkit-mask-image: linear-gradient(to bottom, black 0%, black 78%, transparent 100%); "
        "mask-image: linear-gradient(to bottom, black 0%, black 78%, transparent 100%); "
        "margin-bottom: 1.4rem; display: block;"
        "\"></div>",
        unsafe_allow_html=True
    )

# --- HERO ---
st.markdown("<div class='hero-eyebrow'>You're warmly invited to celebrate the marriage of</div>", unsafe_allow_html=True)
if "&" in COUPLE_NAMES:
    display_names = COUPLE_NAMES.replace("&", "<em>&</em>")
else:
    display_names = COUPLE_NAMES
st.markdown(f"<h1 class='hero-names'>{display_names}</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='hero-date'>{WEDDING_DATE}</div>", unsafe_allow_html=True)
if VENUE:
    st.markdown(f"<div class='hero-venue'>{VENUE.upper()}</div>", unsafe_allow_html=True)
if TIMINGS:
    st.markdown(f"<div class='hero-time'>{TIMINGS}</div>", unsafe_allow_html=True)
if DRESS_CODE:
    st.markdown(f"<div class='hero-dresscode'>Dress code: {DRESS_CODE}</div>", unsafe_allow_html=True)

# Add to Calendar + Directions + Hotels
col_a1, col_a2, col_a3 = st.columns(3)
with col_a1:
    st.download_button(
        "📅 Add to Calendar",
        data=build_ics(),
        file_name="wedding.ics",
        mime="text/calendar",
        use_container_width=True,
    )
with col_a2:
    if VENUE:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={quote(VENUE)}"
        st.link_button("📍 Get Directions", maps_url, use_container_width=True)
with col_a3:
    with st.container(key="hotels_nav_btn"):
        if st.button("🏨 Hotels", use_container_width=True):
            go_to("hotels")
            st.rerun()

st.markdown(SPRIG_SVG, unsafe_allow_html=True)

# --- RSVP FORM ---
st.markdown("<div class='section-label'>Please Let Us Know</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-sub'>Fill in your name below and let us know if you can join us. "
    "Already RSVP'd and need to change your answer? Just submit again with the same name "
    "and it'll update your existing response.</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='rsvp-deadline'>Please kindly respond by 2nd October 2026 at the latest.</div>",
    unsafe_allow_html=True
)

if 'extra_guest_choice' not in st.session_state:
    st.session_state['extra_guest_choice'] = "-None-"

GUEST_COUNT_OPTIONS = {"-None-": 0, "+1": 1, "+2": 2, "+3": 3}

extra_guest_choice = st.selectbox(
    "RSVP on behalf of the rest of your party — how many additional guests? (up to 3)",
    list(GUEST_COUNT_OPTIONS.keys()),
    key="extra_guest_choice"
)
extra_guest_count = GUEST_COUNT_OPTIONS[extra_guest_choice]

with st.form("rsvp_form"):
    st.markdown("<div class='guest-tag'>Your Name</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        g1_first = st.text_input("First Name", key="g1_first")
    with col2:
        g1_last = st.text_input("Last Name", key="g1_last")

    extra_guest_fields = []
    if extra_guest_count > 0:
        st.markdown("<div class='guest-tag'>RSVP on behalf of the rest of your party</div>", unsafe_allow_html=True)
        for i in range(extra_guest_count):
            st.markdown(f"<div class='guest-subtag'>Guest {i + 2}</div>", unsafe_allow_html=True)
            colA, colB = st.columns(2)
            with colA:
                gf = st.text_input("First Name", key=f"g{i + 2}_first")
            with colB:
                gl = st.text_input("Last Name", key=f"g{i + 2}_last")
            extra_guest_fields.append((gf, gl))

    notes = st.text_area(
        "Dietary Requirements (optional)",
        height=80
    )

    st.write("")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        attending_btn = st.form_submit_button("🥂 Joyfully Attending", type="primary")
    with col_btn2:
        not_attending_btn = st.form_submit_button("Regretfully Decline", type="secondary")

    if attending_btn or not_attending_btn:
        status = "Attending" if attending_btn else "Not Attending"

        if not g1_first or not g1_last:
            st.error("Please enter your first and last name above.")
        else:
            df = load_rsvp_data()
            full_name = f"{g1_first.strip()} {g1_last.strip()}"
            additional_names = [f"{f} {l}" for f, l in extra_guest_fields if f and l]

            entry = {
                "Guest 1": full_name,
                "Additional Guests": ", ".join(additional_names) if additional_names else "—",
                "Party Size": 1 + len(additional_names),
                "Status": status,
                "Notes": notes if notes else "—",
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            match_mask = df["Guest 1"].astype(str).str.strip().str.lower() == full_name.strip().lower()

            if match_mask.any():
                match_index = df[match_mask].index[0]
                for key, value in entry.items():
                    df.at[match_index, key] = value
                save_rsvp_data(df)
                is_update = True
            else:
                df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
                save_rsvp_data(df)
                is_update = False

            if status == "Attending":
                msg = "updated" if is_update else "recorded"
                st.success(f"Thank you, {g1_first} — we've {msg} your RSVP. Can't wait to celebrate with you! 🌸")
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

        df = load_rsvp_data()

        if len(df) > 0:
            total_responses = len(df)
            attending_guest_count = int(pd.to_numeric(df.loc[df['Status'] == 'Attending', 'Party Size'], errors='coerce').sum())
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric(label="Total Responses", value=total_responses)
            with col_m2:
                st.metric(label="Total Attending", value=attending_guest_count)

            search_term = st.text_input("🔍 Search guests by name", key="guest_search")
            if search_term:
                search_mask = (
                    df["Guest 1"].astype(str).str.contains(search_term, case=False, na=False)
                    | df["Additional Guests"].astype(str).str.contains(search_term, case=False, na=False)
                )
                display_df = df[search_mask]
            else:
                display_df = df

            st.dataframe(display_df, use_container_width=True)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download responses as CSV", csv, "rsvp_responses.csv", "text/csv")

            st.write("---")
            st.markdown("#### Remove an Entry")

            entry_labels = [
                f"{i} — {row['Guest 1']} ({row['Status']})"
                for i, row in df.iterrows()
            ]
            selected_label = st.radio("Select an entry to remove", entry_labels, key="delete_select")
            selected_index = entry_labels.index(selected_label)
            selected_df_index = df.index[selected_index]

            if 'pending_delete' not in st.session_state:
                st.session_state['pending_delete'] = None

            # If a different entry is picked after a pending confirmation, reset it
            if st.session_state['pending_delete'] is not None and st.session_state['pending_delete'] != selected_df_index:
                st.session_state['pending_delete'] = None

            if st.session_state['pending_delete'] is None:
                if st.button("🗑️ Remove Entry", key="delete_request"):
                    st.session_state['pending_delete'] = selected_df_index
                    st.rerun()
            else:
                target = df.loc[st.session_state['pending_delete']]
                st.warning(f"Remove **{target['Guest 1']}**'s RSVP? This can't be undone.")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    if st.button("✅ Yes, remove it", key="delete_confirm", type="primary"):
                        df = df.drop(index=st.session_state['pending_delete']).reset_index(drop=True)
                        save_rsvp_data(df)
                        st.session_state['pending_delete'] = None
                        st.success("Entry removed.")
                        st.rerun()
                with col_c2:
                    if st.button("Cancel", key="delete_cancel", type="secondary"):
                        st.session_state['pending_delete'] = None
                        st.rerun()
        else:
            st.write("No RSVPs submitted yet.")
    elif host_password:
        st.error("Incorrect password.")
