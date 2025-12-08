# user_dashboard/user_app.py
import streamlit as st
import requests
import os

# 1. Page Configuration: Sets the browser tab title, icon, and centered layout
st.set_page_config(
    page_title="Feedback Portal",
    page_icon="⭐",
    layout="centered"
)

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# 2. Custom CSS: Injecting styles for a cleaner button and removing default clutter
st.markdown("""
    <style>
    /* Style the main submit button to look like a call-to-action */
    div.stButton > button:first-child {
        background-color: #0068c9; /* Professional Blue */
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #0053a6;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Add subtle border to the text area */
    .stTextArea textarea {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Header Section
st.title("💬 Leave a Review")
st.markdown("We value your feedback! Please rate your experience and let us know how we can improve.")
st.divider()

# 4. Main Form Container (Card Style)
with st.container(border=True):
    
    # Rating Section
    st.subheader("How was your experience?")
    # 'st.feedback' is available in Streamlit >= 1.35.0
    # It returns an integer index (0=1 star, 4=5 stars)
    rating_idx = st.feedback("stars")
    
    # Review Section
    st.subheader("Detailed Feedback")
    review = st.text_area(
        "Your review",
        placeholder="Tell us what you liked or what went wrong...",
        height=150,
        label_visibility="collapsed" # Hides the label for a cleaner look
    )

    # 5. Submission Logic with Visual Feedback
    if st.button("Submit Review", use_container_width=True):
        # Validation
        if rating_idx is None:
            st.warning("Please select a star rating to proceed.")
        elif not review.strip():
            st.warning("Please write a short review before submitting.")
        else:
            # Prepare payload (st.feedback is 0-indexed, so we add 1)
            payload = {"rating": rating_idx + 1, "review": review}
            
            # Show a loading spinner while communicating with API
            with st.spinner("Analyzing your feedback..."):
                try:
                    resp = requests.post(f"{API_BASE}/submit_review", json=payload, timeout=5)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success("✅ Thank you! Your review has been submitted.")
                        
                        # Display AI response in a neat expander
                        with st.expander("View AI Response", expanded=True):
                            st.info(data.get("user_response", "No specific response generated."))
                    else:
                        st.error(f"⚠️ Server Error: {resp.status_code}")
                        st.caption(f"Details: {resp.text}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Connection Error: Could not reach the server.")
                    st.caption(f"Is the API running at `{API_BASE}`?")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")