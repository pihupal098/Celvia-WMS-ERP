import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time

# --- PAGE CONFIGURATION & GLASSMORPHISM UI ---
st.set_page_config(page_title="AI E-Com Intelligence Pro", layout="wide", page_icon="🚀")

# 👇 NEW PRO API KEY PRE-FILLED 👇
GEMINI_API_KEY = "AIzaSyC0ozBfgQ5UTyqGKWbAx0qlkguQqu89KaY" 

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

st.markdown("""
<style>
/* Premium Crystal Glassmorphism */
.glass-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.85) 0%, rgba(240, 248, 255, 0.4) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 1);
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 12px 40px rgba(31, 38, 135, 0.12);
    margin-bottom: 25px;
}
.main-score { font-size: 3.5rem; font-weight: 900; line-height: 1; }
.score-green { color: #10b981; }
.score-yellow { color: #f59e0b; }
.score-red { color: #ef4444; }
.italic-text { font-style: italic; color: #475569; }
.highlight-qty { background: rgba(239, 68, 68, 0.1); color: #ef4444; padding: 3px 12px; border-radius: 20px; font-weight: 900; border: 1px solid rgba(239, 68, 68, 0.2); }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🚀 Pro Intelligence")
st.sidebar.success("✅ Gemini Pro Engine Connected")
st.sidebar.markdown("---")
st.sidebar.markdown("**Decision Weights:**\n- 💎 Quality: 40%\n- ⚠️ Defects: 30%\n- 📦 Packing: 15%\n- 📈 Trends: 15%")

# --- MAIN HEADER ---
st.title("📊 E-Com Business Strategist (Pro Version)")
st.markdown("<p style='color: #64748b; font-size: 16px; font-weight: 800; font-style: italic;'>Analyzing every micro-detail to make you the Top Seller.</p>", unsafe_allow_html=True)

def analyze_reviews_with_ai(review_text):
    # Using the most advanced flash model for speed and accuracy
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Act as a Senior E-commerce Growth Consultant. Analyze these customer reviews deeply.
    Calculate a 100-Point Health Score using this weightage: Quality(40), Defects(30), Packaging(15), Trends(15).
    
    REVIEWS:
    {review_text}
    
    Respond STRICTLY in JSON:
    {{
      "score": 0-100,
      "verdict": "Winner" or "Needs Fix" or "Liquidate",
      "breakdown": {{"quality": 0-40, "defects": 0-30, "packaging": 0-15, "value": 0-15}},
      "summary": "3 bullet points summary in Italic style",
      "issue_matrix": [{{"tag": "Defect", "desc": "Broken parts", "count": 10}}],
      "actions": ["Step 1", "Step 2"]
    }}
    """
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": str(e)}

tab1, tab2 = st.tabs(["🏢 My Seller Dashboard", "🕵️ Competitor Intelligence"])

# ==========================================
# TAB 1: SELLER DATA (CSV)
# ==========================================
with tab1:
    st.markdown("### 📤 Internal Review Analysis")
    uploaded_file = st.file_uploader("Upload Seller Review CSV", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        rev_col = next((c for c in df.columns if 'review' in c.lower()), None)
        date_col = next((c for c in df.columns if 'date' in c.lower()), None)
        
        if rev_col:
            st.success(f"📦 Data Loaded: {len(df)} Reviews Found.")
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df = df.sort_values(by=date_col, ascending=False)
            
            if st.button("🚀 Run Deep Pro Analysis", type="primary"):
                with st.spinner("AI is dissecting reviews..."):
                    top_reviews = "\n".join(df[rev_col].dropna().head(80).astype(str))
                    data = analyze_reviews_with_ai(top_reviews)
                    
                    if "error" not in data:
                        score = data['score']
                        clr = "score-green" if score >= 80 else "score-yellow" if score >= 55 else "score-red"
                        
                        st.markdown(f"""
                        <div class="glass-card" style="text-align: center;">
                            <div style="font-size: 18px; font-weight: 800; color: #64748b;">PRODUCT HEALTH SCORE</div>
                            <div class="main-score {clr}">{score}<span style="font-size: 1.5rem; color: #94a3b8;">/100</span></div>
                            <h2 style="margin-top: 5px;">{data['verdict']}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown("<div class='glass-card'><h4>📊 Weighted Score</h4>", unsafe_allow_html=True)
                            b = data['breakdown']
                            st.progress(b['quality']/40, f"Quality: {b['quality']}/40")
                            st.progress(b['defects']/30, f"Defects: {b['defects']}/30")
                            st.progress(b['packaging']/15, f"Packaging: {b['packaging']}/15")
                            st.progress(b['value']/15, f"Value: {b['value']}/15")
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        with c2:
                            st.markdown(f"<div class='glass-card'><h4>📝 Summary</h4><p class='italic-text'>{data['summary']}</p></div>", unsafe_allow_html=True)

                        c3, c4 = st.columns(2)
                        with c3:
                            st.markdown("<div class='glass-card'><h4>🚨 Critical Issue Matrix</h4>", unsafe_allow_html=True)
                            for issue in data['issue_matrix']:
                                st.markdown(f"<span class='highlight-qty'>{issue['count']}</span> <b>{issue['desc']}</b>", unsafe_allow_html=True)
                                st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        with c4:
                            st.markdown("<div class='glass-card'><h4>✅ Actionable Checklist</h4>", unsafe_allow_html=True)
                            for act in data['actions']:
                                st.checkbox(act, key=act)
                            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: BUYER DATA (Links)
# ==========================================
with tab2:
    st.markdown("### 🕵️ Competitor Weakness Finder")
    target_url = st.text_input("Paste Competitor Link (Flipkart/Amazon):")
    
    st.warning("⚠️ Phase 3 Integration: Scraper API will fetch data from this link in real-time.")
    
    if st.button("🔍 Analyze Competitor"):
        if target_url:
            with st.spinner("Extracting Competitor Reviews..."):
                # Simulated reviews for demo based on common diecast car issues
                mock_revs = "Paint quality is bad. Scale is not 1:18 as claimed. Box was crushed. Doors don't open."
                data = analyze_reviews_with_ai(mock_revs)
                
                st.markdown(f"""
                <div class="glass-card">
                    <h3 style="color: #ef4444;">Competitor Vulnerability: {data['score']}/100</h3>
                    <p class="italic-text"><b>AI Observation:</b> {data['summary']}</p>
                    <hr>
                    <h4>How to Beat Them:</h4>
                    <ul>
                """, unsafe_allow_html=True)
                for a in data['actions']:
                    st.markdown(f"<li><i>{a}</i></li>", unsafe_allow_html=True)
                st.markdown("</ul></div>", unsafe_allow_html=True)
