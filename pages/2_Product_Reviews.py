import streamlit as st
import pandas as pd
import google.generativeai as genai
import json
import time
import re

st.set_page_config(page_title="AI E-Com Intelligence", layout="wide", page_icon="🧠")

# 👇 AAPKI ASLI KEY YAHAN FIT HO GAYI HAI 👇
GEMINI_API_KEY = "AIzaSyC0ozBfgQ5UTyqGKWbAx0qlkguQqu89KaY" 

# ==========================================
# 🚀 AUTO-DETECT ENGINE (The Game Changer)
# ==========================================
active_model_name = None
api_error_message = None

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # RADAR: Directly fetching officially alive models from Google Servers
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if available_models:
            # Finding the fastest 'flash' model automatically
            flash_models = [m for m in available_models if 'flash' in m.lower()]
            # Lock the latest available working model
            active_model_name = flash_models[-1] if flash_models else available_models[0]
        else:
            api_error_message = "API Connected but no Generative Models available on this key."
    except Exception as e:
        err_str = str(e)
        if "API_KEY_INVALID" in err_str or "400" in err_str:
            api_error_message = "🚨 API KEY GALAT HAI! Kripya Google AI Studio se 'Copy' button daba kar exact paste karein."
        else:
            api_error_message = f"Network/Server Error: {err_str}"

# --- CSS STYLING ---
st.markdown("""
<style>
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

# --- SIDEBAR DIAGNOSTICS ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=60)
st.sidebar.title("⚙️ System Config")

# INSTANT API CHECKER UI
if active_model_name:
    st.sidebar.success(f"✅ AI Engine Online\n\n🤖 Live Connected to:\n`{active_model_name.replace('models/', '')}`")
else:
    st.sidebar.error(api_error_message)

st.sidebar.markdown("---")
st.sidebar.markdown("**How the 100-Point Algorithm Works:**")
st.sidebar.markdown("- 🟢 40%: Quality & Sentiment\n- 🔴 30%: Defect Rate\n- 📦 15%: Packaging\n- 💸 15%: Value/Trends")

# --- MAIN HEADER ---
st.title("🧠 The E-Com Intelligence Dashboard")
st.markdown("<p style='color: #64748b; font-size: 16px; font-weight: bold;'>Data-driven decisions only. Kill bad products, scale the winners.</p>", unsafe_allow_html=True)

# --- PROGRESS BAR HELPER (Prevents UI Crash) ---
def safe_progress(value, max_val):
    try:
        val = float(value)
    except:
        val = 0.0
    val = max(0.0, min(val, float(max_val))) 
    return val / max_val, f"{int(val)}/{max_val}"

# --- THE AI BRAIN (STRICT & LOCKED) ---
def analyze_reviews_with_ai(review_data_text, model_id):
    prompt = f"""
    Act as a Fortune 500 E-commerce Analyst. I am giving you raw customer reviews.
    Analyze them deeply and calculate a 100-Point Product Health Score based on these exact weights:
    1. Quality & Sentiment (40 Points)
    2. Defect & Issue Rate (30 Points) - Deduct heavily for recurring defects.
    3. Packaging & Delivery (15 Points)
    4. Value for Money & New Trends (15 Points)

    You MUST output ONLY valid JSON format. Do not use backticks or add any conversational text.
    Use this exact JSON schema:
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

    REVIEWS DATA:
    {review_data_text}
    """
    try:
        # PULLING THE DETECTED MODEL
        model = genai.GenerativeModel(
            model_id,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(prompt)
        text_output = response.text
        
        # BULLETPROOF DATA FILTER
        match = re.search(r'\{.*\}', text_output, re.DOTALL)
        if match:
            clean_json = match.group(0)
            return json.loads(clean_json)
        else:
            return {"error": "AI response blocked. Invalid JSON format.", "raw_response": text_output}
            
    except Exception as e:
        return {"error": str(e), "raw_response": "Model crashed during execution."}

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
                if not active_model_name:
                    st.error(f"❌ Analysis Blocked. Please check Sidebar: {api_error_message}")
                else:
                    with st.spinner(f"AI Matrix Analyzing (Engine: {active_model_name.replace('models/', '')})... 🧠"):
                        ai_data = analyze_reviews_with_ai(reviews_text, active_model_name)
                        
                        if "error" in ai_data:
                            st.error(f"❌ Error Occurred: {ai_data['error']}")
                            with st.expander("Click to view Raw Developer Log"):
                                st.write(ai_data.get('raw_response', 'No data'))
                        else:
                            score = ai_data.get('total_score', ai_data.get('score', 0))
                            category = ai_data.get('category', 'Analyzed')
                            bd = ai_data.get('score_breakdown') or {}
                            
                            color_class = "score-green" if score >= 80 else "score-yellow" if score >= 55 else "score-red"
                            
                            st.markdown(f"""
                            <div class="glass-card" style="text-align: center;">
                                <h2>100-Point Product Health Score</h2>
                                <div class="{color_class}">{score}
