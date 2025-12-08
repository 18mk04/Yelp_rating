import streamlit as st
import requests
import os
import pandas as pd
import altair as alt

# 1. Page Configuration: Sets the title and uses the full screen width
st.set_page_config(
    page_title="Review Admin Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS to tweak spacing (optional)
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    </style>
""", unsafe_allow_html=True)

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("🔧 Dashboard Controls")
    st.write("Filter the incoming reviews data.")
    
    with st.form("filter_form"):
        min_stars = st.slider("Minimum Stars", 1, 5, 1)
        limit = st.number_input("Fetch Limit", 10, 500, 100)
        submitted = st.form_submit_button("Refresh Data", type="primary")

# --- Main Dashboard Logic ---
st.title("📊 Admin Dashboard — Reviews")

# Fetch Data
params = {"min_stars": min_stars, "limit": limit}

try:
    # Use spinner for visual feedback during network calls
    with st.spinner("Fetching reviews..."):
        resp = requests.get(f"{API_BASE}/reviews", params=params)
    
    if resp.status_code != 200:
        st.error(f"❌ Failed to fetch reviews. Status: {resp.status_code}")
        st.stop()

    reviews_data = resp.json()
    
    if not reviews_data:
        st.info("No reviews found matching the criteria.")
        st.stop()

    # Convert to DataFrame for easier manipulation and charting
    df = pd.DataFrame(reviews_data)

    # --- KPI Section ---
    st.subheader("Overview")
    kpi1, kpi2, kpi3 = st.columns(3)

    avg_rating = df['rating'].mean()
    total_reviews = len(df)
    pending_summaries = len(df[df['summary'].isnull()]) if 'summary' in df.columns else 0

    kpi1.metric("Average Rating", f"{avg_rating:.2f} ⭐")
    kpi2.metric("Total Reviews Fetched", f"{total_reviews}")
    kpi3.metric("Pending Summaries", f"{pending_summaries}", delta_color="inverse")

    st.divider()

    # --- Analytics Section ---
    col_chart, col_recent = st.columns([2, 1])

    with col_chart:
        st.subheader("Rating Distribution")
        # Prepare data for chart
        chart_data = df['rating'].value_counts().reset_index()
        chart_data.columns = ['rating', 'count']
        
        # Altair Chart
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('rating:O', title='Star Rating'),
            y=alt.Y('count:Q', title='Count'),
            color=alt.Color('rating:O', legend=None, scale=alt.Scale(scheme='blues')),
            tooltip=['rating', 'count']
        ).properties(height=300)
        
        st.altair_chart(chart, use_container_width=True)

    with col_recent:
        st.subheader("Quick Stats")
        st.write("Recent Activity Log")
        # Simple table for last few IDs and timestamps
        if 'created_at' in df.columns:
            st.dataframe(
                df[['id', 'rating', 'created_at']].head(5), 
                hide_index=True, 
                use_container_width=True
            )

    st.divider()

    # --- Detailed Reviews Section ---
    st.subheader("📝 Review Management")

    for r in reviews_data:
        # Create a "Card" look using a container with a border
        with st.container(border=True):
            # Header Row of the card
            c1, c2, c3 = st.columns([1, 4, 2])
            with c1:
                st.write(f"**#{r['id']}**")
            with c2:
                # Display stars visually
                st.write("⭐" * r['rating'])
            with c3:
                st.caption(f"📅 {r.get('created_at', 'Unknown date')}")
            
            # Review Content
            st.markdown(f"**Customer Review:**")
            st.info(r['review'], icon="💬")

            # AI Reply Section
            if r.get('user_response'):
                with st.expander("View Auto-Reply"):
                    st.write(r['user_response'])

            # Summary & Action Section (The Admin Workflow)
            has_summary = r.get('summary') and r.get('recommended_action')
            
            if has_summary:
                st.success("**Analysis Complete**")
                col_sum, col_act = st.columns(2)
                col_sum.write(f"**Summary:** {r['summary']}")
                col_act.write(f"**Action:** {r['recommended_action']}")
            else:
                # Action Button
                st.warning("⚠️ Analysis Pending")
                if st.button(f"Generate Summary for #{r['id']}", key=f"btn_{r['id']}", type="secondary"):
                    with st.spinner("Processing with AI..."):
                        try:
                            sresp = requests.post(f"{API_BASE}/admin/summarize/{r['id']}")
                            if sresp.status_code == 200:
                                st.toast(f"Summary generated for #{r['id']}!", icon="✅")
                                st.rerun()
                            else:
                                st.error("Failed to generate summary.")
                        except Exception as e:
                            st.error(f"Connection error: {e}")

except requests.exceptions.ConnectionError:
    st.error(f"❌ Could not connect to API at `{API_BASE}`. Is the backend running?")