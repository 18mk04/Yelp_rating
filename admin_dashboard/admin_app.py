# admin_dashboard/admin_app.py
import streamlit as st
import requests, os
API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.title("Admin Dashboard — Reviews")
st.sidebar.header("Filters")
min_stars = st.sidebar.slider("Min stars", 1, 5, 1)
limit = st.sidebar.number_input("Limit", 10, 500, 100)

if st.button("Refresh"):
    pass

resp = requests.get(f"{API_BASE}/reviews", params={"min_stars": min_stars, "limit": limit})
if resp.status_code != 200:
    st.error("Failed to fetch reviews")
else:
    reviews = resp.json()
    if reviews:
        avg_rating = sum(r['rating'] for r in reviews) / max(1, len(reviews))
    else:
        avg_rating = 0
    st.metric("Average rating (filtered)", f"{avg_rating:.2f}")
    counts = {}
    for r in reviews:
        counts.setdefault(r['rating'], 0)
        counts[r['rating']] += 1
    st.write("Counts by rating:", counts)
    for r in reviews:
        st.markdown("---")
        st.write(f"**#{r['id']}** — {r['rating']} ★  — {r['created_at']}")
        st.write(r['review'])
        st.write("AI reply:", r.get('user_response') or "_none_")
        if not r.get('summary') or not r.get('recommended_action'):
            if st.button(f"Summarize #{r['id']}", key=f"s_{r['id']}"):
                sresp = requests.post(f"{API_BASE}/admin/summarize/{r['id']}")
                if sresp.status_code == 200:
                    st.experimental_rerun()
                else:
                    st.error("Summary failed")
        else:
            st.write("Summary:", r['summary'])
            st.write("Suggested action:", r['recommended_action'])
