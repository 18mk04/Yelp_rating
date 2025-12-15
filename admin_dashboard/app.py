import streamlit as st
import requests
import os
import pandas as pd
import altair as alt

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Admin Review Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CONFIG & ASSETS
# --------------------------------------------------
API_BASE = os.getenv("API_BASE")

# Custom CSS for Professional Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    /* Review Card Styling */
    .review-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Badge Styling */
    .badge-pending {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-done {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    /* Button Tweaks */
    div.stButton > button {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

if not API_BASE:
    st.error("⚠️ `API_BASE` environment variable is not set.")
    st.stop()

# --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ Dashboard Controls")
    
    with st.container(border=True):
        st.write("**Filter Reviews**")
        min_stars = st.slider("Minimum Rating", 1, 5, 1)
        limit = st.number_input("Max Records", 10, 500, 50)
    
    st.divider()
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.caption(f"Connected to: `{API_BASE}`")
    st.caption("v1.2.0 • Admin Panel")

# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------
@st.cache_data(ttl=60) # Cache for 60 seconds to prevent flickering on UI updates
def fetch_reviews(api_base, min_rating, limit_count):
    params = {"min_stars": min_rating, "limit": limit_count}
    try:
        resp = requests.get(f"{api_base}/reviews", params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None

# Fetch Data
reviews_data = fetch_reviews(API_BASE, min_stars, limit)

# --------------------------------------------------
# MAIN DASHBOARD
# --------------------------------------------------
st.title("📊 Review Administration")

if not reviews_data:
    st.warning("No reviews found or unable to connect to backend.")
    st.stop()

df = pd.DataFrame(reviews_data)

# --- KPI SECTION ---
st.markdown("### Overview")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

avg_rating = df['rating'].mean()
total_reviews = len(df)
pending_analysis = df['summary'].isna().sum()
completed_analysis = total_reviews - pending_analysis

kpi1.metric("Total Reviews", total_reviews)
kpi2.metric("Average Rating", f"{avg_rating:.1f}", delta_color="normal")
kpi3.metric("AI Analysis Completed", completed_analysis, delta=f"{completed_analysis} done")
kpi4.metric("Pending Action", pending_analysis, delta=f"-{pending_analysis}", delta_color="inverse")

st.divider()

# --- CHARTS SECTION ---
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Rating Distribution")
    chart_data = df['rating'].value_counts().reset_index()
    chart_data.columns = ["rating", "count"]
    
    # Custom color scale for ratings
    chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("rating:O", title="Star Rating"),
        y=alt.Y("count:Q", title="Number of Reviews"),
        color=alt.Color("rating:O", scale=alt.Scale(scheme="blues"), legend=None),
        tooltip=["rating", "count"]
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)

with c2:
    st.subheader("Action Items")
    # Quick donut chart simulation for status
    status_df = pd.DataFrame({
        'Status': ['Analyzed', 'Pending'],
        'Count': [completed_analysis, pending_analysis]
    })
    
    pie = alt.Chart(status_df).mark_arc(innerRadius=50).encode(
        theta=alt.Theta("Count", stack=True),
        color=alt.Color("Status", scale=alt.Scale(domain=['Analyzed', 'Pending'], range=['#10B981', '#F59E0B'])),
        tooltip=["Status", "Count"]
    ).properties(height=300)
    
    st.altair_chart(pie, use_container_width=True)

# --------------------------------------------------
# DETAILED REVIEW FEED
# --------------------------------------------------
st.subheader("Review Feed")
st.markdown(f"Showing last **{len(df)}** reviews based on filters.")

for r in reviews_data:
    # Card Container
    with st.container():
        # Using Markdown CSS class defined above involves creating a div wrapper, 
        # but here we use Streamlit columns to structure the layout cleanly.
        
        # Determine Status
        has_summary = r.get("summary") is not None
        status_color = "green" if has_summary else "orange"
        status_text = "Analyzed" if has_summary else "Pending Analysis"
        
        # Layout: [Meta Info] | [Main Content] | [Action Panel]
        col_meta, col_content, col_action = st.columns([1.5, 5, 2.5])
        
        with col_meta:
            st.markdown(f"**#{r['id']}**")
            st.markdown(f"{'⭐' * r['rating']}")
            if has_summary:
                st.markdown(f'<span class="badge-done">✔ {status_text}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="badge-pending">⏳ {status_text}</span>', unsafe_allow_html=True)
                
        with col_content:
            st.markdown(f"**Customer Review:**")
            st.info(f"\"{r['review']}\"")
            
            if r.get("user_response"):
                with st.expander("See Auto-Reply"):
                    st.write(r["user_response"])

        with col_action:
            if has_summary:
                with st.container(border=True):
                    st.markdown("**AI Insights**")
                    st.caption("Summary")
                    st.write(r["summary"])
                    st.divider()
                    st.caption("Recommended Action")
                    st.markdown(f"**{r['recommended_action']}**")
            else:
                st.write("") # Spacer
                st.write("") # Spacer
                if st.button(f"✨ Generate Summary", key=f"gen_{r['id']}", use_container_width=True):
                    with st.spinner("Analyzing text..."):
                        try:
                            sresp = requests.post(
                                f"{API_BASE}/admin/summarize/{r['id']}",
                                timeout=10
                            )
                            if sresp.status_code == 200:
                                st.toast("Summary generated successfully!", icon="✅")
                                st.rerun() # Refresh to show new state
                            else:
                                st.error("Analysis failed.")
                        except Exception as e:
                            st.error(f"Connection error: {e}")
        
        st.divider()