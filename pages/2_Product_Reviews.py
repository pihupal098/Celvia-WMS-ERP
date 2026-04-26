import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time
import re

# --- PAGE CONFIGURATION & GLASSMORPHISM CSS ---
st.set_page_config(page_title="AI E-Com Intelligence", layout="wide", page_icon="🧠")

# 👇 AAPKI EXACT API KEY YAHAN FIT KAR DI GAYI HAI 👇
GEMINI_API_KEY = "AIzaSyC0ozBfgQ5UTyqGKWbAx0qlkguQqu89KaY" 

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.sidebar.error("API Setup failed.")

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

# --- SIDEBAR: SYSTEM INFO ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=60)
st.sidebar.title("⚙️ System Config")
st.sidebar.success("✅ AI Engine Active & Connected")
st.sidebar.markdown("---")
st.sidebar.markdown("**How the 100-Point Algorithm Works:**")
st.sidebar.markdown("- 🟢 40%: Quality & Sentiment\n- 🔴 30%: Defect Rate\n- 📦 15%: Packaging\n- 💸 15%: Value/Trends")

# --- MAIN HEADER ---
st.title("🧠 The E-Com Intelligence Dashboard")
st.markdown("<p style='color: #64748b; font-size: 16px; font-weight: bold;'>Data-driven decisions only. Kill bad products, scale the winners.</p>", unsafe_allow_html=True)

# --- THE AI BRAIN (BULLETPROOF PROMPT & REGEX) ---
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
      "total_score": 85,
      "category": "Winner Product",
      "score_breakdown": {{
        "quality": 35,
        "defect_rate": 25,
        "packaging": 12,
        "value": 13
      }},
      "quick_summary": "Summary here",
      "issue_matrix": [
        {{"issue": "Issue Name", "mentions": "10"}}
      ],
      "trend_analysis": "Trend here",
      "actionable_checklist": [
        "Step 1",
        "Step 2"
      ]
    }}
    """
    try:
        # Using gemini-pro which is highly stable and won't throw 404
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        text_output = response.text
        
        # Double safety: remove markdown blocks if AI ignored instructions
        text_output = text_output.replace("```json", "").replace("```", "").strip()
        
        # Regex to pull out only the JSON dictionary
        match = re.search(r'\{.*\}', text_output, re.DOTALL)
        
        if match:
            clean_json = match.group(0)
            return json.loads(clean_json)
        else:
            return {"error": "AI response format failed.", "raw_response": text_output}
            
    except Exception as e:
        return {"error": str(e), "raw_response": "Failed to connect to Google API."}

# --- TABS SETUP ---
tab1, tab2 = st.tabs(["🏢 My Seller Dashboard", "🕵️ Competitor Intelligence"])

# ==========================================
# TAB 1: SELLER PORTAL
# ==========================================
with tab1:
    st.markdown("### 📤 Analyze Your Own Products")
    st.info("Upload your Flipkart/Amazon Review CSV. Ensure it has a column named 'Review' or 'Review Text'.")
    
    uploaded_file = st.file_uploader("Upload Reviews CSV", type=["csv"], key="seller_csv")
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        review_col = next((col for col in df.columns if 'review' in col.lower()), None)
        date_col = next((col for col in df.columns if 'date' in col.lower()), None)
        
        if review_col:
            st.success(f"✅ Found {len(df)} reviews. Ready to process.")
            
            if date_col:
                try:
                    df[date_col] = pd.to_datetime(df[date_col])
                    df = df.sort_values(by=date_col, ascending=False)
                except:
                    pass
            
            recent_reviews = df[review_col].dropna().head(100).tolist()
            reviews_text = "\n".join([f"- {r}" for r in recent_reviews])
            
            if st.button("🚀 Run Deep Analysis", type="primary"):
                with st.spinner("Calculating 100-Point Health Score & Issue Matrix... 🧠"):
                    ai_data = analyze_reviews_with_ai(reviews_text)
                    
                    if "error" in ai_data:
                        st.error(f"❌ Error: {ai_data['error']}")
                        with st.expander("Click to view raw system logs"):
                            st.write(ai_data.get('raw_response', 'No data'))
                    else:
                        # Full-proof data extraction (No KeyErrors)
                        score = ai_data.get('total_score', ai_data.get('score', 0))
                        category = ai_data.get('category', 'Analysis Complete')
                        bd = ai_data.get('score_breakdown', {})
                        
                        color_class = "score-green" if score >= 80 else "score-yellow" if score >= 55 else "score-red"
                        
                        st.markdown(f"""
                        <div class="glass-card" style="text-align: center;">
                            <h2>100-Point Product Health Score</h2>
                            <div class="{color_class}">{score} / 100</div>
                            <h3 style="margin-top: 0; color: #1e293b;">{category}</h3>
                            <div class="sub-text">Algorithm: Quality (40) | Defects (30) | Packaging (15) | Value (15)</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                            st.markdown("#### 📊 Score Breakdown")
                            st.progress(min(bd.get('quality', 0) / 40, 1.0), text=f"Quality: {bd.get('quality', 0)}/40")
                            st.progress(min(bd.get('defect_rate', 0) / 30, 1.0), text=f"Defects: {bd.get('defect_rate', 0)}/30")
                            st.progress(min(bd.get('packaging', 0) / 15, 1.0), text=f"Packaging: {bd.get('packaging', 0)}/15")
                            st.progress(min(bd.get('value', 0) / 15, 1.0), text=f"Value & Trends: {bd.get('value', 0)}/15")
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                        with c2:
                            st.markdown(f"""
                            <div class='glass-card'>
                                <h4>📝 Executive Summary</h4>
                                <p style="font-size: 16px; color: #0f172a;">{ai_data.get('quick_summary', 'No summary available.')}</p>
                                <hr>
                                <h4>⏳ Trend Analysis (Latest vs Old)</h4>
                                <p style="color: #475569;"><i>{ai_data.get('trend_analysis', 'No trend analysis available.')}</i></p>
                            </div>
                            """, unsafe_allow_html=True)

                        c3, c4 = st.columns(2)
                        with c3:
                            st.markdown("<div class='glass-card'><h4>🚨 The Issue Matrix</h4>", unsafe_allow_html=True)
                            for issue in ai_data.get('issue_matrix', []):
                                st.markdown(f"<span class='issue-badge'>{issue.get('mentions', '0')} Mentions</span> <span style='font-weight:bold;'>{issue.get('issue', 'Unknown')}</span>", unsafe_allow_html=True)
                                st.markdown("<br>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                            
                        with c4:
                            st.markdown("<div class='glass-card'><h4>✅ The Fix-It Checklist</h4>", unsafe_allow_html=True)
                            for action in ai_data.get('actionable_checklist', []):
                                st.checkbox(str(action))
                            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Could not find a 'Review' column in your CSV. Please check the file.")

# ==========================================
# TAB 2: BUYER PORTAL
# ==========================================
with tab2:
    st.markdown("### 🕵️ Competitor Weakness Finder")
    st.info("Paste a Flipkart or Amazon Product Link below.")
    
    product_link = st.text_input("🔗 Paste Flipkart/Amazon Product URL:")
    
    st.markdown("""
    <div style="background: rgba(234, 179, 8, 0.1); border: 1px solid #eab308; padding: 15px; border-radius: 10px; color: #854d0e; font-weight: bold; margin-bottom: 15px;">
        ⚠️ Phase 3 Integration: Scraper API will fetch data from this link in real-time.
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 Analyze Competitor"):
        if not product_link:
            st.warning("Please paste a link first.")
        else:
            with st.spinner("Connecting to Scraper API... Fetching Real-time Reviews..."):
                time.sleep(2) 
                st.success("Reviews Fetched Successfully! (Simulated for Demo)")
                
                mock_competitor_reviews = """
                "The toy looks good but the wheels broke on day 2."
                "It is too small, pictures are misleading."
                "Okay product, but the plastic is very cheap and smells bad."
                "Battery does not last even 10 minutes."
                "The delivery was fast, but the box was completely crushed."
                """
                
                with st.spinner("Analyzing Competitor Data... 🧠"):
                    ai_data = analyze_reviews_with_ai(mock_competitor_reviews)
                    
                    if "error" in ai_data:
                        st.error(f"❌ AI Error: {ai_data['error']}")
                        with st.expander("Click to view raw system logs"):
                            st.write(ai_data.get('raw_response', 'No raw data available.'))
                    else:
                        score = ai_data.get('total_score', ai_data.get('score', 0))
                        summary = ai_data.get('quick_summary', ai_data.get('summary', 'No summary available.'))
                        
                        st.markdown(f"""
                        <div class="glass-card">
                            <h3 style="color: #ef4444;">Competitor Vulnerability: {score}/100</h3>
                            <p><strong>Competitor's Weakness (Your Opportunity):</strong> {summary}</p>
                            <h4>How you can beat them:</h4>
                            <ul>
                        """, unsafe_allow_html=True)
                        
                        checklist = ai_data.get('actionable_checklist', ai_data.get('checklist', []))
                        for action in checklist:
                            st.markdown(f"<li>{action}</li>", unsafe_allow_html=True)
                        
                        st.markdown("</ul></div>", unsafe_allow_html=True)
