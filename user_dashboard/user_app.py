# user_dashboard/user_app.py
import streamlit as st
import requests, os
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.title("Leave a review")
rating = st.selectbox("Star rating", [5,4,3,2,1], index=0)
review = st.text_area("Your review", height=150)
if st.button("Submit"):
    payload = {"rating": int(rating), "review": review}
    resp = requests.post(f"{API_BASE}/submit_review", json=payload)
    if resp.status_code == 200:
        data = resp.json()
        st.success("Thanks — AI response:")
        st.write(data.get("user_response"))
    else:
        st.error(f"Error: {resp.status_code} {resp.text}")
