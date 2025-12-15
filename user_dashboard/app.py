import streamlit as st
import requests
import os

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
# CUSTOM CSS (PROFESSIONAL UI)
# --------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Font & Background */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #F3F4F6; /* Light gray background */
    }

    /* Main Card Container */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
        max-width: 600px;
    }

    /* Styling the container to look like a Card */
    div[data-testid="stVerticalBlock"] > div:has(div.stMarkdown) {
        background-color: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Buttons */
    div.stButton > button {
        background-color: #2563EB;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }
    div.stButton > button:active {
        transform: scale(0.98);
    }

    /* Text Area */
    .stTextArea textarea {
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        font-size: 15px;
    }
    .stTextArea textarea:focus {
        border-color: #2563EB;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
    }

    /* Hide Streamlit Boilerplate */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}


    .ai-box {
        background-color: #F0F9FF;
        border-left: 4px solid #0EA5E9;
        padding: 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-top: 1rem;
        color: #0C4A6E;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
API_BASE = os.getenv(
    "API_BASE",
    "https://yelp-rating.onrender.com"  # ✅ DEPLOYED BACKEND
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "ai_reply" not in st.session_state:
    st.session_state.ai_reply = ""

def reset():
    st.session_state.submitted = False
    st.session_state.ai_reply = ""

# --------------------------------------------------
# MAIN CONTAINER (CARD)
# --------------------------------------------------
# We use a container to apply the "white card" visual effect
with st.container():

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------
    st.markdown("<h1 style='text-align: center; font-size: 2rem; margin-bottom: 0.5rem;'>Feedback Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280; margin-bottom: 2rem;'>We are committed to improving. How was your experience today?</p>", unsafe_allow_html=True)

    # --------------------------------------------------
    # SUCCESS VIEW
    # --------------------------------------------------
    if st.session_state.submitted:
        st.success("🎉 Thank you! Your feedback has been recorded.")

        if st.session_state.ai_reply:
            st.markdown(f"""
            <div class="ai-box">
                <div style="font-weight: 700; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;">
                   Response
                </div>
                <div style="line-height: 1.6;">
                    {st.session_state.ai_reply}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.write("") # Spacer
        if st.button("Submit Another Review", use_container_width=True):
            reset()
            st.rerun()

    # --------------------------------------------------
    # FORM VIEW
    # --------------------------------------------------
    else:
        st.markdown("### Rate your experience")
        rating_idx = st.feedback("stars")
        
        # Add a visual label for the selected rating
        labels = ["Very Poor", "Poor", "Average", "Good", "Excellent"]
        if rating_idx is not None:
            st.caption(f"You selected: **{labels[rating_idx]}**")
        else:
            st.caption("Select a star rating above")

        st.markdown("### Written Review")
        review = st.text_area(
            "Your feedback",
            placeholder="Tell us what went well or what can be improved...",
            height=150,
            label_visibility="collapsed" # Hide the default label for a cleaner look
        )

        st.write("") # Spacer

        if st.button("Submit Feedback", use_container_width=True):
            if rating_idx is None:
                st.toast("⚠️ Please select a star rating first.", icon="⭐")
                st.stop()

            if not review.strip():
                st.toast("⚠️ Please write a short review.", icon="✍️")
                st.stop()

            payload = {
                "rating": rating_idx + 1,
                "review": review.strip()
            }

            with st.spinner("Analyzing feedback..."):
                try:
                    resp = requests.post(
                        f"{API_BASE}/submit_review",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=20
                    )

                    if resp.status_code == 200:
                        data = resp.json()

                        # ✅ CORRECT KEY
                        st.session_state.ai_reply = data.get(
                            "user_response",
                            "Thank you for your feedback."
                        )

                        st.session_state.submitted = True
                        st.rerun()

                    else:
                        st.error("Server error")
                        st.code(resp.text)

                except requests.exceptions.RequestException:
                    st.error(
                        "Unable to reach the server.\n\n"
                        "If this is the first request, the backend may be waking up."
                    )