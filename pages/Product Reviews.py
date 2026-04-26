import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time

# --- PAGE CONFIGURATION & GLASSMORPHISM CSS ---
st.set_page_config(page_title="AI E-Com Intelligence", layout="wide", page_icon="🧠")

st.markdown("""
<style>
/* Premium Glassmorphism Cards */
.glass-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(240, 248, 255, 0.4) 100%);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.9);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
    margin-bottom: 20px;
}
.score-green { color: #10b981; font-weight: 900; font-size: 2.5rem; }
.score-yellow { color: #f59e0b; font-weight: 900; font-size: 2.5rem; }
.score-red { color: #ef4444; font-weight: 900; font-size: 2.5rem; }
.sub-text { font-size: 14px; color: #475569; font-style: italic; }
.issue-badge { background: rgba(239, 68, 68, 0.1); color: #ef4444; padding: 4px 10px; border-radius: 12px; font-weight: bold; border: 1px solid rgba(239, 68, 68, 0.3); }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: API SETUP ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=60)
st.sidebar.title("⚙️ System Config")
api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")
st.sidebar.markdown("---")
st.sidebar.markdown("**How the 100-Point Algorithm Works:**")
st.sidebar.markdown("- 🟢 40%: Quality & Sentiment\n- 🔴 30%: Defect Rate\n- 📦 15%: Packaging\n- 💸 15%: Value/Trends")

if api_key:
    genai.configure(api_key=api_key)

# --- MAIN HEADER ---
st.title("🧠 The E-Com Intelligence Dashboard")
st.markdown("<p style='color: #64748b; font-size: 16px; font-weight: bold;'>Data-driven decisions only. Kill bad products, scale the winners.</p>", unsafe_allow_html=True)

# --- THE AI BRAIN (PROMPT ENGINEERING) ---
def analyze_reviews_with_ai(review_data_text):
    prompt = f"""
    Act as a Fortune 500 E-commerce Analyst. I am giving you raw customer reviews.
    Analyze them deeply and calculate a 100-Point Product Health Score based on these exact weights:
    1. Quality & Sentiment (40 Points)
    2. Defect & Issue Rate (30 Points) - Deduct heavily for recurring defects.
    3. Packaging & Delivery (15 Points)
    4. Value for Money & New Trends (15 Points)

    REVIEWS DATA:
    {review_data_text}

    You MUST respond ONLY with a valid JSON object in the exact format below. Do not include markdown formatting or backticks around the JSON.
    {{
      "total_score": <number 0-100>,
      "category": "<'Winner Product' or 'Needs Fixes' or 'Dead Zone - Kill It'>",
      "score_breakdown": {{
        "quality": <number 0-40>,
        "defect_rate": <number 0-30>,
        "packaging": <number 0-15>,
        "value": <number 0-15>
      }},
      "quick_summary": "<3 sentences summarizing the product's reality>",
      "issue_matrix": [
        {{"issue": "<Issue Name>", "mentions": <estimated percentage or count>}}
      ],
      "trend_analysis": "<Compare old vs new reviews based on the data provided>",
      "actionable_checklist": [
        "<Actionable Step 1>",
        "<Actionable Step 2>"
      ]
    }}
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        # Clean JSON if AI adds markdown backticks
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": str(e), "raw_response": response.text if 'response' in locals() else "API Failure"}

# --- TABS SETUP ---
tab1, tab2 = st.tabs(["🏢 Seller Portal (Internal Analytics)", "🕵️ Buyer Portal (Competitor Spy)"])

# ==========================================
# TAB 1: SELLER PORTAL (CSV Upload)
# ==========================================
with tab1:
    st.markdown("### 📤 Analyze Your Own Products")
    st.info("Upload your Flipkart/Amazon Review CSV. Ensure it has a column named 'Review' or 'Review Text'.")
    
    uploaded_file = st.file_uploader("Upload Reviews CSV", type=["csv"], key="seller_csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Try to find Review and Date columns dynamically
        review_col = next((col for col in df.columns if 'review' in col.lower()), None)
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        
        if review_col:
            st.success(f"✅ Found {len(df)} reviews. Analyzing...")
            
            # Sort Latest to Old if Date column exists
            if date_col:
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    df = df.sort_values(by=date_col, ascending=False)
                except:
                    pass
            
            # Prepare data for AI (Take top 100 recent reviews to save API tokens)
            recent_reviews = df[review_col].dropna().head(100).tolist()
            reviews_text = "\n".join([f"- {r}" for r in recent_reviews])
            
            if st.button("🚀 Run Deep Analysis (Seller Data)", type="primary"):
                if not api_key:
                    st.error("⚠️ Enter Gemini API Key in the sidebar.")
                else:
                    with st.spinner("Calculating 100-Point Health Score & Issue Matrix... 🧠"):
                        ai_data = analyze_reviews_with_ai(reviews_text)
                        
                        if "error" in ai_data:
                            st.error(f"AI Parsing Error: Please try again. Details: {ai_data['error']}")
                        else:
                            # --- RENDER DASHBOARD ---
                            score = ai_data.get('total_score', 0)
                            color_class = "score-green" if score >= 80 else "score-yellow" if score >= 55 else "score-red"
                            
                            # 1. SCORE BANNER
                            st.markdown(f"""
                            <div class="glass-card" style="text-align: center;">
                                <h2>100-Point Product Health Score</h2>
                                <div class="{color_class}">{score} / 100</div>
                                <h3 style="margin-top: 0; color: #1e293b;">{ai_data.get('category', '')}</h3>
                                <div class="sub-text">Algorithm: Quality (40) | Defects (30) | Packaging (15) | Value (15)</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 2. BREAKDOWN & SUMMARY
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                                st.markdown("#### 📊 Score Breakdown")
                                bd = ai_data.get('score_breakdown', {})
                                st.progress(bd.get('quality', 0) / 40, text=f"Quality: {bd.get('quality')}/40")
                                st.progress(bd.get('defect_rate', 0) / 30, text=f"Defects: {bd.get('defect_rate')}/30")
                                st.progress(bd.get('packaging', 0) / 15, text=f"Packaging: {bd.get('packaging')}/15")
                                st.progress(bd.get('value', 0) / 15, text=f"Value & Trends: {bd.get('value')}/15")
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                            with c2:
                                st.markdown(f"""
                                <div class='glass-card'>
                                    <h4>📝 Executive Summary</h4>
                                    <p style="font-size: 16px; color: #0f172a;">{ai_data.get('quick_summary', '')}</p>
                                    <hr>
                                    <h4>⏳ Trend Analysis (Latest vs Old)</h4>
                                    <p style="color: #475569;"><i>{ai_data.get('trend_analysis', '')}</i></p>
                                </div>
                                """, unsafe_allow_html=True)

                            # 3. ISSUE MATRIX & ACTION PLAN
                            c3, c4 = st.columns(2)
                            with c3:
                                st.markdown("<div class='glass-card'><h4>🚨 The Issue Matrix (Root Causes)</h4>", unsafe_allow_html=True)
                                for issue in ai_data.get('issue_matrix', []):
                                    st.markdown(f"<span class='issue-badge'>{issue.get('mentions')} Mentions</span> <span style='font-weight:bold;'>{issue.get('issue')}</span>", unsafe_allow_html=True)
                                    st.markdown("<br>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                            with c4:
                                st.markdown("<div class='glass-card'><h4>✅ The Fix-It Checklist</h4>", unsafe_allow_html=True)
                                for action in ai_data.get('actionable_checklist', []):
                                    st.checkbox(action)
                                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Could not find a 'Review' column in your CSV. Please check the file.")


# ==========================================
# TAB 2: BUYER PORTAL (Link Integration Phase)
# ==========================================
with tab2:
    st.markdown("### 🕵️ Competitor Spy (Link Analyzer)")
    st.info("Paste a Flipkart or Amazon Product Link below. The system will use APIs to scrape reviews and analyze the competitor's weaknesses.")
    
    product_link = st.text_input("🔗 Paste Flipkart/Amazon Product URL:")
    
    # ⚠️ APIFY / RAPIDAPI INTEGRATION PLACEHOLDER ⚠️
    # Yahan asli system mein RapidAPI ka request jayega jo URL se data nikalega.
    st.markdown("""
    <div style="background: rgba(56, 189, 248, 0.1); border: 1px dashed #38bdf8; padding: 15px; border-radius: 10px;">
        <strong>Phase 3 Network Hook:</strong> Jab aap 'Scan Competitor' dabayenge, toh backend ek <code>GET</code> request bhejeha <em>RapidAPI Amazon/Flipkart Scraper</em> ko. Scraper 200 recent reviews JSON format mein return karega, jisko humara Gemini AI upar wale same 100-Point Algorithm se process kar dega!
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Scan Competitor Weaknesses"):
        if not product_link:
            st.warning("Please paste a link first.")
        else:
            with st.spinner("Connecting to Scraper API... Bypassing Security... Fetching Reviews..."):
                time.sleep(2) # Simulating API delay
                st.success("Reviews Fetched Successfully! (Simulated)")
                
                # Mock competitor reviews for demonstration of the flow
                mock_competitor_reviews = """
                "The toy looks good but the wheels broke on day 2."
                "It is too small, pictures are misleading."
                "Okay product, but the plastic is very cheap and smells bad."
                "Battery does not last even 10 minutes."
                """
                
                with st.spinner("Analyzing Competitor Data... 🧠"):
                    ai_data = analyze_reviews_with_ai(mock_competitor_reviews)
                    if "error" not in ai_data:
                        score = ai_data.get('total_score', 0)
                        
                        st.markdown(f"""
                        <div class="glass-card">
                            <h3>Competitor Health Score: <span style="color:#ef4444;">{score}/100</span></h3>
                            <p><strong>Competitor's Weakness (Your Opportunity):</strong> {ai_data.get('quick_summary')}</p>
                            <h4>How you can beat them:</h4>
                            <ul>
                        """, unsafe_allow_html=True)
                        
                        for action in ai_data.get('actionable_checklist', []):
                            st.markdown(f"<li>{action}</li>", unsafe_allow_html=True)
                        
                        st.markdown("</ul></div>", unsafe_allow_html=True)
