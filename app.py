"""Crucible AI - Streamlit Web Application.
Multi-Agent Stress-Testing System for Startup Ideas (100% Free Tier).
"""

import streamlit as st
from src.config import get_gemini_api_key, DEFAULT_MODEL
from src.orchestrator import CrucibleOrchestrator

# Set page configuration
st.set_page_config(
    page_title="Crucible AI | Multi-Agent Idea Stress-Tester",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 800;
        color: #FF4B4B;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #888888;
        margin-bottom: 25px;
    }
    .agent-box {
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 15px;
        border: 1px solid #e0e0e0;
        background-color: #f9f9f9;
    }
    .stMetric {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar Configuration ----------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/flame.png", width=64)
    st.title("Crucible AI")
    st.caption("Adversarial Multi-Agent Stress-Testing")

    st.markdown("---")
    st.markdown("### 🔑 API Configuration")
    
    env_key = get_gemini_api_key(st)
    user_api_key = st.text_input(
        "Google Gemini API Key (100% Free):",
        value=env_key,
        type="password",
        help="Get a free key at https://aistudio.google.com/ with zero credit card required.",
    )
    
    if not user_api_key:
        st.warning("👉 [Get a free key here](https://aistudio.google.com/) and paste it above.")
    else:
        st.success("API Key detected!")

    selected_model = st.selectbox(
        "Gemini Model (Free Tier):",
        options=["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 🤖 The 4 Adversarial Agents")
    st.markdown("""
    - **💼 Skeptical Investor**: Attacks market size, monetization & TAM.
    - **😤 Angry Customer**: Exposes UX friction, apathy & switching costs.
    - **🛠️ Pragmatic Engineer**: Flags scaling bottlenecks & tech debt.
    - **🌐 Market Researcher**: Uses real DuckDuckGo web search data.
    - **⚖️ Chief Judge**: Weighs arguments and renders a final scorecard.
    """)

# ---------------- Main Page ----------------
st.markdown('<p class="main-header">🔥 CRUCIBLE AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Put your startup idea, feature, or project hypothesis through a brutal multi-agent stress-test.</p>', unsafe_allow_html=True)

# Preset Quick-Pick Ideas
st.markdown("**💡 Or test with a sample idea:**")
col_s1, col_s2, col_s3 = st.columns(3)
sample_idea = ""
if col_s1.button("🐶 Autonomous Drone Dog Walker"):
    sample_idea = "An on-demand service where automated tethered drones walk dogs in suburban neighborhoods with camera tracking and automated treat dispensers."
if col_s2.button("💼 Tinder for Technical Co-Founders"):
    sample_idea = "A swipe-based matchmaking app for startup founders where profiles are verified with GitHub commit histories, equity split preferences, and personality tests."
if col_s3.button("🎙️ AI Podcast to Daily Newsletter"):
    sample_idea = "A SaaS tool that automatically listens to 2-hour niche tech podcasts, removes sponsor fluff, and emails subscribers a 3-minute actionable executive summary."

# Input Idea Form
idea_input = st.text_area(
    "Pitch your idea, thesis, or product feature:",
    value=sample_idea,
    height=120,
    placeholder="e.g., A mobile app where freelance designers bid live on micro-projects with escrow smart contracts...",
)

human_counter = st.text_input(
    "Founder's defense / extra context (Optional Human-in-the-Loop):",
    placeholder="e.g., We already have exclusive distribution through 5 design universities.",
    help="Add key advantages or counter-points you want the Chief Judge to consider.",
)

start_button = st.button("🚀 Run Multi-Agent Stress Test", type="primary", use_container_width=True)

# ---------------- Processing & Output ----------------
if start_button:
    if not user_api_key.strip():
        st.error("Please enter a valid Google Gemini API key in the sidebar to run the stress test.")
    elif not idea_input.strip():
        st.warning("Please type or select an idea to test.")
    else:
        status_box = st.status("Initializing agent debate...", expanded=True)
        
        def update_progress(msg: str):
            status_box.write(msg)

        orchestrator = CrucibleOrchestrator(api_key=user_api_key, model_name=selected_model)
        
        with st.spinner("Agents are fiercely analyzing and debating your idea..."):
            results = orchestrator.run_stress_test(
                idea=idea_input,
                human_counter=human_counter,
                progress_callback=update_progress,
            )
        
        status_box.update(label="Stress test complete!", state="complete", expanded=False)

        # Store in session state for downloading/viewing
        st.session_state["crucible_results"] = results

# Display Results if available
if "crucible_results" in st.session_state:
    res = st.session_state["crucible_results"]
    
    st.markdown("---")
    st.subheader("⚔️ The Adversarial Debate")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💼 Skeptical Investor",
        "😤 Angry Customer",
        "🛠️ Pragmatic Engineer",
        "🌐 Market Researcher",
        "🔍 Web Evidence",
    ])
    
    with tab1:
        st.markdown(res["investor_critique"])
    with tab2:
        st.markdown(res["customer_critique"])
    with tab3:
        st.markdown(res["engineer_critique"])
    with tab4:
        st.markdown(res["researcher_critique"])
    with tab5:
        st.markdown("**Live DuckDuckGo Search Results fed to the Researcher:**")
        st.text(res["search_data"])

    st.markdown("---")
    st.subheader("⚖️ The Chief Judge Verdict & Scorecard")
    st.markdown(res["judge_scorecard"])

    # Downloadable Report
    report_content = f"""# CRUCIBLE AI: VENTURE STRESS-TEST REPORT

## 💡 Submitted Idea
{res['idea']}

## 💼 Skeptical Investor Critique
{res['investor_critique']}

## 😤 Angry Customer Critique
{res['customer_critique']}

## 🛠️ Pragmatic Engineer Critique
{res['engineer_critique']}

## 🌐 Market Researcher Intelligence
{res['researcher_critique']}

## ⚖️ Executive Chief Judge Scorecard
{res['judge_scorecard']}
"""
    st.download_button(
        label="📥 Download Full Stress-Test Report (Markdown)",
        data=report_content,
        file_name="crucible_ai_scorecard.md",
        mime="text/markdown",
    )

