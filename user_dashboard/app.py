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
# UI
# --------------------------------------------------
st.title("Feedback Portal")
st.caption("We are committed to improving. How was your experience today?")

# --------------------------------------------------
# SUCCESS VIEW
# --------------------------------------------------
if st.session_state.submitted:
    st.success("Thank you! Your feedback has been recorded.")

    if st.session_state.ai_reply:
        st.info(f"🤖 AI Response:\n\n{st.session_state.ai_reply}")

    if st.button("Submit Another Review"):
        reset()
        st.rerun()

# --------------------------------------------------
# FORM VIEW
# --------------------------------------------------
else:
    rating_idx = st.feedback("stars")

    review = st.text_area(
        "Your feedback",
        placeholder="Tell us what went well or what can be improved",
        height=150
    )

    if st.button("Submit Feedback", use_container_width=True):
        if rating_idx is None:
            st.warning("Please select a rating.")
            st.stop()

        if not review.strip():
            st.warning("Please write a short review.")
            st.stop()

        payload = {
            "rating": rating_idx + 1,
            "review": review.strip()
        }

        with st.spinner("Submitting feedback..."):
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
