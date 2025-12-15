import streamlit as st
import requests
import os
import time

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Feedback Portal",
    page_icon="⭐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# CONFIG & SETUP
# --------------------------------------------------
API_BASE = os.getenv("API_BASE")

# Initialize Session State for form management
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "submit_success" not in st.session_state:
    st.session_state.submit_success = False

def reset_app():
    """Resets the UI to allow a new submission"""
    st.session_state.form_submitted = False
    st.session_state.submit_success = False
    # Rerun to clear widgets is handled by the key increment or manual reset patterns
    # ideally, we just rely on page rerun logic here.

# --------------------------------------------------
# CUSTOM CSS (PROFESSIONAL THEME)
# --------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Global Font Application */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Remove default top padding */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 700px;
    }

    /* Card Styling */
    .stContainer {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f0f2f6;
    }

    /* Button Styling */
    div.stButton > button {
        background-color: #2563EB; /* Professional Blue */
        color: white;
        border-radius: 8px;
        height: 3.2em;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 5px rgba(37, 99, 235, 0.2);
    }
    div.stButton > button:hover {
        background-color: #1D4ED8;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3);
    }
    div.stButton > button:active {
        transform: translateY(0px);
    }

    /* Secondary Button (Reset) */
    div.stButton > button.secondary-btn {
        background-color: #F3F4F6;
        color: #374151;
    }

    /* Text Area Styling */
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        font-size: 16px;
        padding: 12px;
    }
    .stTextArea textarea:focus {
        border-color: #2563EB;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.1);
    }

    /* Headers */
    h1 {
        font-weight: 700;
        color: #111827;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    p {
        color: #6B7280;
        font-size: 1.05rem;
    }
    
    /* Hide Streamlit Branding elements for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# APP LOGIC
# --------------------------------------------------

# Check Config
if not API_BASE:
    st.error("⚠️ System Configuration Error: `API_BASE` is missing.")
    st.stop()

# --- HEADER ---
st.markdown("<h1 style='text-align: center;'>Feedback Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-bottom: 30px;'>We are committed to improving. How was your experience today?</p>", unsafe_allow_html=True)

# --- SUCCESS VIEW ---
if st.session_state.form_submitted and st.session_state.submit_success:
    with st.container():
        # Using columns to center the success message visually
        c1, c2, c3 = st.columns([1, 6, 1])
        with c2:
            st.markdown(
                """
                <div style="text-align: center; padding: 40px; background: #ECFDF5; border-radius: 12px; border: 1px solid #A7F3D0;">
                    <div style="font-size: 50px;">🎉</div>
                    <h3 style="color: #065F46; margin-top: 10px;">Thank You!</h3>
                    <p style="color: #047857;">Your feedback has been successfully recorded.</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            st.write("") # Spacer
            if st.button("Submit Another Review", use_container_width=True):
                reset_app()
                st.rerun()

# --- FORM VIEW ---
else:
    with st.container():
        
        # 1. Rating Section
        st.markdown("### Rate your experience")
        rating_idx = st.feedback("stars")
        
        # Dynamic label based on rating
        rating_labels = {
            0: "Very Poor 😞",
            1: "Poor 😕",
            2: "Average 😐",
            3: "Good 🙂",
            4: "Excellent 🤩"
        }
        
        if rating_idx is not None:
            st.caption(f"You rated: **{rating_labels[rating_idx]}**")
        else:
            st.caption("Click the stars to rate.")

        st.write("") # Spacer

        # 2. Review Section
        review = st.text_area(
            "Review Details",
            placeholder="What did you like? What can we improve?",
            height=150,
            label_visibility="hidden" # Hidden because we use the placeholder and header context
        )

        st.write("") # Spacer

        # 3. Submit Action
        if st.button("Submit Feedback", use_container_width=True):
            
            # Validation
            if rating_idx is None:
                st.toast("⚠️ Please select a star rating first.", icon="⭐")
            elif not review.strip():
                st.toast("⚠️ Please write a brief review.", icon="✍️")
            else:
                payload = {
                    "rating": rating_idx + 1,
                    "review": review.strip()
                }

                with st.spinner("Sending feedback..."):
                    try:
                        resp = requests.post(
                            f"{API_BASE}/submit_review",
                            json=payload,
                            timeout=10
                        )

                        if resp.status_code == 200:
                            st.session_state.form_submitted = True
                            st.session_state.submit_success = True
                            st.rerun()
                        else:
                            st.error(f"Server Error: {resp.status_code}")
                            st.code(resp.text)
                    
                    except requests.exceptions.RequestException:
                        st.error("Unable to reach the server. Please check your internet connection.")