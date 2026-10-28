"""Crucible AI - Streamlit Web Application.
Multi-Agent Stress-Testing System for Ideas.
"""

import streamlit as st
from src.config import (
    get_gemini_api_key,
    AVAILABLE_MODELS,
    MODEL_LABEL_TO_ID,
    DEFAULT_MODEL,
)
from src.orchestrator import CrucibleOrchestrator

# Set page configuration
st.set_page_config(
    page_title="Crucible AI | Multi-Agent Idea Stress-Tester",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for clean layout
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 2px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 20px;
    }
    .stMetric {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("Crucible AI")
    st.caption("Adversarial Multi-Agent Stress-Testing")
    st.markdown("---")

    st.markdown("### The 4 Adversarial Agents")
    st.markdown("""
    - **Skeptical Investor**: Questions market size, unit economics, monetization, and defensibility.
    - **Angry Customer**: Exposes UX friction, user apathy, switching inertia, and unmet expectations.
    - **Pragmatic Engineer**: Identifies architecture bottlenecks, API latency, infrastructure costs, and technical risks.
    - **Market Researcher**: Analyzes competitors, past failures, and real market data using live search.
    - **Chief Judge**: Synthesizes the debate into a scorecard with key risks, actionable fixes, and a final verdict.
    """)

# ---------------- Main Page ----------------
st.markdown('<p class="main-header">Crucible AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-agent adversarial stress-testing system for startup ideas and product hypotheses.</p>', unsafe_allow_html=True)

# Prompt Templates
PROMPT_TEMPLATES = {
    "Choose a prompt template to fill...": "",
    "Startup Pitch": (
        "Problem:\n"
        "[What specific painful problem does this solve?]\n\n"
        "Target Audience:\n"
        "[Who experiences this problem and pays for it?]\n\n"
        "Proposed Solution:\n"
        "[How does your product solve it?]\n\n"
        "Monetization Model:\n"
        "[How does the business make money?]\n\n"
        "Key Advantage / Moat:\n"
        "[Why can't competitors easily copy this?]"
    ),
    "Product Feature": (
        "Feature Name:\n"
        "[Name of the feature or capability]\n\n"
        "User Problem It Solves:\n"
        "[Why are users asking for this or struggling today?]\n\n"
        "How It Works:\n"
        "[Step-by-step user workflow]\n\n"
        "Expected Impact:\n"
        "[Key metrics: retention, revenue, or efficiency]"
    ),
    "B2B SaaS Tool": (
        "Target Industry / Buyer:\n"
        "[e.g., Mid-market CFOs, DevOps Leads, HR Managers]\n\n"
        "Workflow Bottleneck:\n"
        "[The manual or inefficient process today]\n\n"
        "Software Solution:\n"
        "[How your software automates or resolves it]\n\n"
        "Pricing & Packaging:\n"
        "[e.g., $99/seat/month, usage-based]\n\n"
        "Incumbent Alternatives:\n"
        "[Tools they currently use instead]"
    ),
    "Consumer Mobile App": (
        "App Concept:\n"
        "[Core consumer proposition in one sentence]\n\n"
        "Core Habit / Hook:\n"
        "[Why will users open this app every day?]\n\n"
        "Target Demographic:\n"
        "[Age, interests, lifestyle]\n\n"
        "Acquisition & Distribution:\n"
        "[How you get the first 10,000 users]\n\n"
        "Revenue Model:\n"
        "[Freemium, subscription, in-app purchases, ads]"
    ),
}

# Template selection callback
if "idea_text" not in st.session_state:
    st.session_state["idea_text"] = ""

def apply_template():
    selected = st.session_state.get("template_dropdown", "")
    if selected in PROMPT_TEMPLATES and PROMPT_TEMPLATES[selected]:
        st.session_state["idea_text"] = PROMPT_TEMPLATES[selected]

col_label, col_dropdown = st.columns([1.5, 1.5])
with col_label:
    st.markdown("**Pitch your idea, thesis, or product feature:**")
with col_dropdown:
    st.selectbox(
        "Prompt template option:",
        options=list(PROMPT_TEMPLATES.keys()),
        key="template_dropdown",
        on_change=apply_template,
        label_visibility="collapsed",
    )

idea_input = st.text_area(
    label="Pitch your idea, thesis, or product feature:",
    key="idea_text",
    height=170,
    placeholder="Type your idea here or select a prompt template above to fill...",
    label_visibility="collapsed",
)

# Model selection and founder defense controls right around the typing place
col_model, col_context = st.columns([1.5, 1.5])
with col_model:
    model_labels = [m["label"] for m in AVAILABLE_MODELS]
    selected_model_label = st.selectbox(
        "Model (highest limits first):",
        options=model_labels,
        index=0,
        help="Choose a Gemini model. Models with higher RPM and daily quotas are listed first.",
    )
    selected_model_id = MODEL_LABEL_TO_ID.get(selected_model_label, DEFAULT_MODEL)

with col_context:
    human_counter = st.text_input(
        "Founder defense / extra context (Optional):",
        placeholder="Add specific advantages or context for the Chief Judge...",
    )

start_button = st.button("Run Test", type="primary", use_container_width=True)

# ---------------- Processing & Output ----------------
if start_button:
    api_key = get_gemini_api_key(st)
    if not api_key:
        st.error("API key not detected. Please make sure GEMINI_API_KEY is configured in your .env file or environment.")
    elif not idea_input.strip():
        st.warning("Please type or fill an idea to test.")
    else:
        status_box = st.status(f"Initializing agent debate using {selected_model_id}...", expanded=True)
        
        def update_progress(msg: str):
            status_box.write(msg)

        orchestrator = CrucibleOrchestrator(api_key=api_key, model_name=selected_model_id)
        
        with st.spinner("Agents are analyzing and debating your idea..."):
            results = orchestrator.run_stress_test(
                idea=idea_input,
                human_counter=human_counter,
                progress_callback=update_progress,
            )
        
        status_box.update(label="Stress test complete.", state="complete", expanded=False)
        st.session_state["crucible_results"] = results

# Display Results if available
if "crucible_results" in st.session_state:
    res = st.session_state["crucible_results"]
    
    st.markdown("---")
    st.subheader("The Adversarial Debate")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Skeptical Investor",
        "Angry Customer",
        "Pragmatic Engineer",
        "Market Researcher",
        "Web Search Data",
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
        st.markdown("**DuckDuckGo Search Results fed to Researcher:**")
        st.text(res["search_data"])

    st.markdown("---")
    st.subheader("Chief Judge Scorecard")
    st.markdown(res["judge_scorecard"])

    # Downloadable Report
    report_content = f"""# CRUCIBLE AI: VENTURE STRESS-TEST REPORT

## Submitted Idea
{res['idea']}

## Skeptical Investor Critique
{res['investor_critique']}

## Angry Customer Critique
{res['customer_critique']}

## Pragmatic Engineer Critique
{res['engineer_critique']}

## Market Researcher Intelligence
{res['researcher_critique']}

## Executive Chief Judge Scorecard
{res['judge_scorecard']}
"""
    st.download_button(
        label="Download Stress-Test Report (Markdown)",
        data=report_content,
        file_name="crucible_ai_scorecard.md",
        mime="text/markdown",
    )
