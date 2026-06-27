#!/usr/bin/env python3
"""
Builder's Black Book - Subcontractor Submission Form
With better error handling
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import gspread

# ================== FILE PATHS ==================
PENDING_CSV = "data/pending_subcontractors.csv"
ASSETS_PATH = "assets"

st.set_page_config(
    page_title="Join Builder's Black Book",
    page_icon="🔧",
    layout="centered"
)

# ================== GOOGLE SHEETS CONNECTION ==================
@st.cache_resource
def get_gsheet_connection():
    try:
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        sheet = gc.open("Builder's Black Book - Pending Submissions").sheet1
        return sheet
    except Exception as e:
        st.error("❌ Unable to connect to the submission system.")
        st.error("Please try again in a few minutes.")
        st.stop()

# Try to connect to Google Sheets
try:
    sheet = get_gsheet_connection()
except:
    sheet = None

# ================== LOGO HEADER ==================
col_logo, col_title = st.columns([1, 4])

with col_logo:
    st.image("https://via.placeholder.com/110x38/1a365d/ffffff?text=BB", width=110)

with col_title:
    st.title("Join Builder's Black Book")
    st.caption("Get considered for projects in the Nashville area")

st.markdown("---")

# ================== INTRO ==================
st.markdown("""
Builder’s Black Book is a private network that connects quality subcontractors with active builders in the Nashville area.

We manually review every submission. If we believe you’re a good fit, we add you to our recommended list and share your information with trusted builders.

Your information stays private — we do not sell or distribute your data.
""")

st.markdown("---")

# ================== FORM ==================
st.subheader("Your Company")

col1, col2 = st.columns(2)

with col1:
    company_name = st.text_input("Company Name *")
    primary_trade = st.multiselect(
        "Primary Trades * (Select all that apply)",
        options=[
            "Framing / Carpentry", "Electrical", "Plumbing", "HVAC",
            "Drywall & Insulation", "Painting", "Roofing", "Flooring",
            "Concrete & Foundations", "Excavation & Site Work", "Masonry",
            "Finish Carpentry / Trim", "Tile & Stone", "Landscaping & Hardscaping"
        ]
    )
    other_trades = st.text_input("Other Trades You Do Well", placeholder="Example: Decks, Fencing, Siding")

with col2:
    areas_served = st.text_input("Main Areas You Work In", placeholder="ZIP codes or neighborhoods")
    website = st.text_input("Website (optional)")

st.subheader("Contact Information")

col3, col4 = st.columns(2)

with col3:
    phone = st.text_input("Phone Number *")
    email = st.text_input("Email Address *")

with col4:
    contact_name = st.text_input("Main Contact Name")

st.subheader("Your Experience")

biggest_project = st.text_input(
    "What’s the biggest project you’ve worked on? (optional)",
    placeholder="Example: $850k custom home, 12-unit townhome project, etc."
)

st.subheader("Verification (Optional)")

portfolio_link = st.text_input(
    "Link to your work (Website, Instagram, Facebook, etc.)",
    placeholder="https://www.yourcompany.com or Instagram link"
)

st.subheader("Licensing & Insurance")

licensed_insured = st.radio(
    "Are you licensed and insured?",
    options=[
        "Yes, I am both licensed and insured",
        "I am licensed but not currently insured",
        "I am not currently licensed or insured"
    ]
)

if licensed_insured != "Yes, I am both licensed and insured":
    st.info("We can connect you with insurance options if needed.")

st.subheader("Additional Information")

notes = st.text_area(
    "Anything else we should know?",
    placeholder="Examples:\n• What makes you reliable\n• Specialties or strengths\n• How you handle larger or more complex projects",
    height=100
)

st.markdown("---")

# ================== SUBMIT BUTTON ==================
submitted = st.button("Submit My Information", type="primary", use_container_width=True)

if submitted:
    if not company_name or not primary_trade or not phone or not email:
        st.error("Please fill out Company Name, Primary Trade(s), Phone, and Email.")
    else:
        new_row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            company_name,
            ", ".join(primary_trade),
            other_trades,
            phone,
            email,
            website,
            areas_served,
            contact_name,
            biggest_project,
            licensed_insured,
            portfolio_link,
            notes
        ]

        # Try to save to Google Sheets
        try:
            if sheet is None:
                st.error("❌ Submission system is currently unavailable.")
                st.error("Please try again in a few minutes or contact us directly.")
            else:
                sheet.append_row(new_row)
                st.success("✅ Thank you! Your information has been submitted for review.")
                st.info("We’ll review your submission and reach out if we think there may be a good project fit.")
        except Exception as e:
            st.error("❌ Something went wrong while saving your submission.")
            st.error(f"Error: {str(e)}")
            st.warning("Please try again in a few minutes.")
