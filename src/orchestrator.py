"""Multi-Agent Orchestrator for Crucible AI."""

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional

from src.agents.llm_client import GeminiClient
from src.agents.prompts import (
    INVESTOR_PROMPT,
    CUSTOMER_PROMPT,
    ENGINEER_PROMPT,
    RESEARCHER_PROMPT,
    JUDGE_PROMPT,
)
from src.tools.search import search_market_data

class CrucibleOrchestrator:
    """Coordinates the 4 adversarial agents and synthesizes via Chief Judge."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.client = GeminiClient(api_key=api_key, model=model_name)

    def run_stress_test(
        self,
        idea: str,
        human_counter: Optional[str] = None,
        progress_callback=None,
    ) -> Dict[str, Any]:
        """
        Executes the full stress test pipeline:
        1. Web Search for competitive landscape.
        2. Parallel execution of Investor, Customer, Engineer, and Researcher.
        3. Human response incorporation (if provided).
        4. Chief Judge evaluation and scorecard.
        """
        results: Dict[str, Any] = {
            "idea": idea,
            "search_data": "",
            "investor_critique": "",
            "customer_critique": "",
            "engineer_critique": "",
            "researcher_critique": "",
            "judge_scorecard": "",
        }

        # Step 1: Web Research Search Query
        if progress_callback:
            progress_callback("🔍 Scanning the web for competitors and market trends...")
        
        search_query = f"{idea[:100]} startup competitors market failure"
        search_results = search_market_data(search_query, max_results=3)
        results["search_data"] = search_results

        # Step 2: Run the 4 Debaters in parallel using ThreadPoolExecutor
        if progress_callback:
            progress_callback("⚔️ Debaters unleashed: Investor, Customer, Engineer & Researcher attacking...")

        def call_investor():
            prompt = f"Stress-test this business idea:\n\n\"{idea}\""
            return self.client.generate(INVESTOR_PROMPT, prompt, temperature=0.7)

        def call_customer():
            prompt = f"Critique this product/idea as an impatient, skeptical customer:\n\n\"{idea}\""
            return self.client.generate(CUSTOMER_PROMPT, prompt, temperature=0.8)

        def call_engineer():
            prompt = f"Point out all technical bottlenecks and architecture headaches with this idea:\n\n\"{idea}\""
            return self.client.generate(ENGINEER_PROMPT, prompt, temperature=0.6)

        def call_researcher():
            prompt = (
                f"Analyze competitors and real-world market precedents for this idea:\n\n"
                f"IDEA:\n\"{idea}\"\n\n"
                f"LIVE WEB SEARCH DATA:\n{search_results}"
            )
            return self.client.generate(RESEARCHER_PROMPT, prompt, temperature=0.5)

        with ThreadPoolExecutor(max_workers=4) as executor:
            future_investor = executor.submit(call_investor)
            future_customer = executor.submit(call_customer)
            future_engineer = executor.submit(call_engineer)
            future_researcher = executor.submit(call_researcher)

            results["investor_critique"] = future_investor.result()
            results["customer_critique"] = future_customer.result()
            results["engineer_critique"] = future_engineer.result()
            results["researcher_critique"] = future_researcher.result()

        # Step 3: Chief Judge Synthesis
        if progress_callback:
            progress_callback("⚖️ Chief Judge reviewing debate arguments and rendering verdict...")

        human_section = ""
        if human_counter and human_counter.strip():
            human_section = f"\n\nFOUNDER'S COUNTER-ARGUMENT / EXTRA CONTEXT:\n\"{human_counter.strip()}\""

        judge_input = (
            f"ORIGINAL FOUNDER IDEA:\n\"{idea}\"\n"
            f"{human_section}\n\n"
            f"--- DEBATE TRANSCRIPT ---\n\n"
            f"### 💼 SKEPTICAL INVESTOR CRITIQUE:\n{results['investor_critique']}\n\n"
            f"### 😤 ANGRY CUSTOMER CRITIQUE:\n{results['customer_critique']}\n\n"
            f"### 🛠️ PRAGMATIC ENGINEER CRITIQUE:\n{results['engineer_critique']}\n\n"
            f"### 🌐 MARKET RESEARCHER CRITIQUE & EVIDENCE:\n{results['researcher_critique']}\n\n"
            f"Synthesize the debate and deliver your structured Executive Crucible Scorecard."
        )

        results["judge_scorecard"] = self.client.generate(JUDGE_PROMPT, judge_input, temperature=0.4)

        if progress_callback:
            progress_callback("✅ Crucible analysis complete!")

        return results

