import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time
import re

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="AI E-Com Intelligence", layout="wide", page_icon="🧠")

# 👇 APNI COPY KI HUI API KEY YAHAN PASTE KAREIN 👇
GEMINI_API_KEY = "AIzaSyCHRRH_LgVpMZI5lVjygPz-naWq6zsdsGA" 

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- 2. CSS STYLING ---
st.markdown("""
<style>
.glass-card { background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 15px; padding: 20px; margin-bottom: 20px; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
.score-green { color: #10b981; font-weight: 900; font-size: 2.5rem; }
.score-yellow { color: #f59e0b; font-weight: 900; font-size: 2.5rem; }
.score-red { color: #ef4444; font-weight: 900; font-size: 2.5rem; }
.issue-badge { background: #fee2e2; color: #ef4444; padding: 4px 10px; border-radius: 12px; font-weight: bold; border: 1px solid #fca5a5; margin-right: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR ---
st.sidebar.title("⚙️ System Config")
st.sidebar.success("✅ Engine: gemini-1.5-flash (Free Tier)")
st.sidebar.markdown("---")
st.sidebar.markdown("**Score Weights:**\n- 🟢 Quality: 40\n- 🔴 Defects: 30\n- 📦 Packaging: 15\n- 💸 Value: 15")

# --- 4. HEADER ---
st.title("🧠 The E-Com Intelligence Dashboard")
st.markdown("Data-driven decisions only. Kill bad products, scale the winners.")

# --- 5. SAFETY HELPERS ---
def safe_progress(value, max_val):
    try:
        val = float(value)
    except:
        val = 0.0
    val = max(0.0, min(val, float(max_val))) 
    return val / max_val, f"{int(val)}/{max_val}"

# --- 6. AI BRAIN (SYNTAX-ERROR PROOF) ---
def analyze_reviews_with_ai(reviews_text):
    # String addition used instead of f-strings to prevent SyntaxError crashes
    p1 = "Act as an E-commerce Analyst. Calculate a 100-Point Product Health Score based on: Quality (40), Defects (30), Packaging (15), Value (15).\n\n"
    p2 = "You MUST output ONLY valid JSON format. Do not write any other text.\n"
    p3 = '{"total_score": 85, "category": "Winner Product", "score_breakdown": {"quality": 35, "defect_rate": 25, "packaging": 12, "value": 13}, "quick_summary": "Summary text", "issue_matrix": [{"issue": "Broken part", "mentions": "10"}], "trend_analysis": "Trend text", "actionable_checklist": ["Do this", "Do that"]}\n\n'
    p4 = "REVIEWS DATA TO ANALYZE:\n" + reviews_text
    
    prompt = p1 + p2 + p3 + p4

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_output = response.text
        
        # Extract JSON using Regex
        match = re.search(r'\{.*\}', text_output, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            return {"error": "AI response blocked. Invalid formatting.", "raw": text_output}
            
    except Exception as e:
        return {"error": f"API Connection Failed: {str(e)}"}

# --- 7. TABS ---
tab1, tab2 = st.tabs(["🏢 My Seller Dashboard", "🕵️ Competitor Intelligence"])

# ==========================================
# TAB 1: SELLER PORTAL
# ==========================================
with tab1:
    st.markdown("### 📤 Analyze Your Own Products")
    uploaded_file = st.file_uploader("Upload Reviews CSV", type=["csv"], key="seller_csv")
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            review_col = next((col for col in df.columns if 'review' in col.lower()), None)
            
            if review_col:
                st.success(f"✅ Found {len(df)} reviews. Ready to process.")
                recent_reviews = df[review_col].dropna().head(80).tolist()
                reviews_str = "\n".join([f"- {r}" for r in recent_reviews])
                
                if st.button("🚀 Run Deep Analysis", type="primary"):
                    with st.spinner("Analyzing data with gemini-1.5-flash... 🧠"):
                        ai_data = analyze_reviews_with_ai(reviews_str)
                        
                        if "error" in ai_data:
                            st.error(f"❌ {ai_data['error']}")
                        else:
                            score = ai_data.get('total_score', 0)
                            category = ai_data.get('category', 'Analyzed')
                            bd = ai_data.get('score_breakdown') or {}
                            
                            color_class = "score-green" if score >= 80 else "score-yellow" if score >= 55 else "score-red"
                            
                            st.markdown(f"""
                            <div class="glass-card" style="text-align: center;">
                                <h2>100-Point Product Health Score</h2>
                                <div class="{color_class}">{score} / 100</div>
                                <h3>{category}</h3>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            c1, c2 = st.columns([1, 2])
                            with c1:
                                st.markdown("<div class='glass-card'><h4>📊 Score Breakdown</h4>", unsafe_allow_html=True)
                                for key, max_val, title in [('quality', 40, 'Quality'), ('defect_rate', 30, 'Defects'), ('packaging', 15, 'Packaging'), ('value', 15, 'Value')]:
                                    val, txt = safe_progress(bd.get(key, 0), max_val)
                                    st.progress(val, text=f"{title}: {txt}")
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                            with c2:
                                st.markdown(f"""
                                <div class='glass-card'>
                                    <h4>📝 Executive Summary</h4><p>{ai_data.get('quick_summary', 'N/A')}</p><hr>
                                    <h4>⏳ Trend Analysis</h4><p>{ai_data.get('trend_analysis', 'N/A')}</p>
                                </div>
                                """, unsafe_allow_html=True)

                            c3, c4 = st.columns(2)
                            with c3:
                                st.markdown("<div class='glass-card'><h4>🚨 Issue Matrix</h4>", unsafe_allow_html=True)
                                for issue in ai_data.get('issue_matrix', []):
                                    st.markdown(f"<span class='issue-badge'>{issue.get('mentions', '0')}</span> {issue.get('issue', 'Issue')}<br><br>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
                                
                            with c4:
                                st.markdown("<div class='glass-card'><h4>✅ Fix-It Checklist</h4>", unsafe_allow_html=True)
                                for action in ai_data.get('actionable_checklist', []):
                                    st.checkbox(str(action))
                                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("❌ 'Review' column not found in CSV.")
        except Exception as e:
            st.error(f"CSV Reading Error: {str(e)}")

# ==========================================
# TAB 2: BUYER PORTAL
# ==========================================
with tab2:
    st.markdown("### 🕵️ Competitor Weakness Finder")
    product_link = st.text_input("🔗 Paste Flipkart/Amazon Product URL:")
    
    if st.button("🔍 Analyze Competitor"):
        if not product_link:
            st.warning("Please paste a link first.")
        else:
            with st.spinner("Connecting to Scraper & AI Engine..."):
                time.sleep(1) 
                # Mock Reviews for Demo
                mock_reviews = "Wheels broke on day 2.\nToo small.\nPlastic is very cheap and smells bad.\nBattery dies fast.\nBox crushed."
                
                ai_data = analyze_reviews_with_ai(mock_reviews)
                
                if "error" in ai_data:
                    st.error(f"❌ {ai_data['error']}")
                else:
                    score = ai_data.get('total_score', 0)
                    st.markdown(f"""
                    <div class="glass-card">
                        <h3 style="color: #ef4444;">Vulnerability Score: {score}/100</h3>
                        <p><strong>Weakness:</strong> {ai_data.get('quick_summary', 'N/A')}</p>
                        <h4>How to beat them:</h4><ul>
                    """, unsafe_allow_html=True)
                    for action in ai_data.get('actionable_checklist', []):
                        st.markdown(f"<li>{action}</li>", unsafe_allow_html=True)
                    st.markdown("</ul></div>", unsafe_allow_html=True)
