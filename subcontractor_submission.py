#!/usr/bin/env python3
"""
Builder's Black Book - Subcontractor Submission Form
Primary: Supabase | Fallback: CSV
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from supabase import create_client, Client

# ================== FILE PATHS ==================
PENDING_CSV = Path("data/pending_subcontractors.csv")
ASSETS_PATH = Path("assets")

# Create data folder if it doesn't exist
PENDING_CSV.parent.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="Join Builder's Black Book",
    page_icon="🔧",
    layout="centered"
)

# ================== SUPABASE CONNECTION ==================
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        return None


# ================== LOGO HEADER ==================
col_logo, col_title = st.columns([1, 4])

with col_logo:
    logo_path = ASSETS_PATH / "logo.svg"
    if logo_path.exists():
        st.image(str(logo_path), width=110)
    else:
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

# ================== FORM FIELDS ==================
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
        # Prepare the data row
        new_row = {
            "company_name": company_name,
            "primary_trade": ", ".join(primary_trade),
            "other_trades": other_trades,
            "phone": phone,
            "email": email,
            "website": website,
            "areas_served": areas_served,
            "contact_name": contact_name,
            "biggest_project": biggest_project,
            "licensed_insured": licensed_insured,
            "portfolio_link": portfolio_link,
            "notes": notes
        }

        saved_successfully = False
        saved_to = ""

        # Try Supabase first
        try:
            supabase = get_supabase_client()
            if supabase:
                supabase.table("subcontractor_submissions").insert(new_row).execute()
                saved_successfully = True
                saved_to = "Supabase"
        except Exception as e:
            pass  # Will try CSV fallback

        # Fallback to CSV if Supabase fails
        if not saved_successfully:
            try:
                if PENDING_CSV.exists():
                    df = pd.read_csv(PENDING_CSV)
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                else:
                    df = pd.DataFrame([new_row])

                df.to_csv(PENDING_CSV, index=False)
                saved_successfully = True
                saved_to = "CSV file (backup)"
            except Exception as e:
                st.error("❌ Failed to save your submission.")
                st.error("Please try again in a few minutes or contact us directly.")
                st.stop()

        # Success message
        if saved_successfully:
            st.success("✅ Thank you! Your information has been submitted for review.")
            st.info(f"Your submission was saved to: **{saved_to}**")
            st.info("We’ll review your submission and reach out if we think there may be a good project fit.")
