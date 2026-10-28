# 🔥 Crucible AI (Roast My Idea)
> **A multi-agent adversarial stress-testing system for startup ideas, pitch decks, and project theses.** Built 100% from scratch on a permanent **$0.00 Free Tier**.

---

## 🌟 Why This Stands Out
Most AI projects are simple "chat with PDF" wrappers. **Crucible AI** is a true **agentic multi-agent system** with specialized personas, adversarial debate dynamics, tool use (live DuckDuckGo web search), human-in-the-loop interjections, and an authoritative judge synthesis with a 0-100 feasibility scorecard.

---

## 🤖 The Multi-Agent Council

| Agent | Avatar | Persona & Role | Objective |
| :--- | :---: | :--- | :--- |
| **Skeptical Investor** | 💼 | Hard-nosed VC | Relentlessly attacks TAM, unit economics, monetization, and defensibility. |
| **Angry Customer** | 😤 | Cynical end-user | Exposes friction, user apathy, switching inertia, and privacy concerns. |
| **Pragmatic Engineer**| 🛠️ | Staff Architect | Flags scaling bottlenecks, API latency, infrastructure costs, and edge cases. |
| **Market Researcher** | 🌐 | Competitive Intel | Executes live DuckDuckGo web searches to identify real competitors & past post-mortems. |
| **Chief Judge** | ⚖️ | Strategy Magistrate | Synthesizes the debate into a 0-100 Scorecard, Top 3 Fatal Risks, and a Go/No-Go verdict. |

---

## 💸 100% Free Tech Stack
- **LLM Engine:** Google Gemini 2.5 Flash / 1.5 Flash (via [Google AI Studio Free Tier](https://aistudio.google.com/) — 15 RPM, 1,500 RPD, 0 credit card needed).
- **Web Search Tool:** DuckDuckGo Search (`duckduckgo-search` library — 100% free, no API key).
- **Agent Orchestrator:** Python `ThreadPoolExecutor` parallel async execution.
- **Frontend UI:** Streamlit.
- **Hosting & Deployment:** Streamlit Community Cloud (100% free forever).

---

## 🚀 Quickstart Guide (Run Locally)

### 1. Clone & Setup Virtual Environment
```bash
cd /Users/macbookpro/Documents/project/agents/crucible_ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and paste your free key from [Google AI Studio](https://aistudio.google.com/):
```env
GEMINI_API_KEY="AIzaSy..."
```

### 3. Launch the App
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser!

---

## 🌐 Free Cloud Deployment (Streamlit Community Cloud)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Crucible AI"
   git branch -M main
   git remote add origin https://github.com/<your-username>/crucible-ai.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
   - Click **"New App"** -> choose your repo `crucible-ai` and file `app.py`.
   - Click **"Advanced Settings"** -> Under **Secrets**, paste:
     ```toml
     GEMINI_API_KEY = "AIzaSy..."
     ```
   - Click **"Deploy!"**
   - You get a live public URL (e.g. `https://crucible-ai.streamlit.app`) to share with anyone!

---

## 🛡️ Failure Modes Tested & Handled
- **Web Search Failure**: Graceful fallback to parametric intelligence if rate-limited.
- **Gemini Rate Limit / Version**: Auto-fallback between Gemini 2.5 Flash and 1.5 Flash.
- **Echo Chamber Prevention**: Independent parallel agent executions ensure agents do not bias one another before debate synthesis.

