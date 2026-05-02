from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from research_agent import run_research_agent
from sentiment_agent import run_sentiment_agent
from financial_agent import run_financial_agent
import concurrent.futures
import os

load_dotenv(override=True)


class StratumAIState(TypedDict):
    company_name:       str
    research_findings:  str
    sentiment_findings: str
    financial_findings: str
    final_report:       str


# ─────────────────────────────────────────
# PARALLEL EXECUTION NODE
# Runs all 3 agents at the same time
# ─────────────────────────────────────────
def parallel_research_node(state: StratumAIState) -> StratumAIState:
    company = state["company_name"]
    print(f"🚀 Running 3 agents in parallel for: {company}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_research  = executor.submit(run_research_agent,  company)
        future_sentiment = executor.submit(run_sentiment_agent, company)
        future_financial = executor.submit(run_financial_agent, company)

        research_findings  = future_research.result()
        sentiment_findings = future_sentiment.result()
        financial_findings = future_financial.result()

    print("✅ All 3 agents done")
    return {
        "research_findings":  research_findings,
        "sentiment_findings": sentiment_findings,
        "financial_findings": financial_findings,
    }


def writer_node(state: StratumAIState) -> StratumAIState:
    print("✍️  Writer Agent running...")

    llm = ChatMistralAI(
        model="mistral-small-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0
    )

    prompt = f"""You are a senior business analyst with over decades of experience.

You have received intelligence reports from three specialized agents
about the company: {state["company_name"]}

--- RESEARCH FINDINGS ---
{state["research_findings"]}

--- SENTIMENT FINDINGS ---
{state["sentiment_findings"]}

--- FINANCIAL FINDINGS ---
{state["financial_findings"]}

Write a professional Competitive Intelligence Brief with these sections:

# {state["company_name"]} - Intelligence Brief

## 1. Executive Summary
(3-4 sentences summarizing the most important things to know)

## 2. Key Developments
(Recent news and product updates that matter)

## 3. Market Sentiment
(What customers, employees and the public think)

## 4. Financial and Growth Signals
(Funding, hiring trends, revenue signals)

## 5. Strategic Implications
(What this all means - where is this company headed?)

## 6. Watch List
(3 specific things to monitor about this company in the next 90 days)

Be concise, specific, and use bullet points inside each section."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_report": response.content}


# ─────────────────────────────────────────
# BUILD GRAPH
# ─────────────────────────────────────────
def build_graph():
    graph = StateGraph(StratumAIState)

    graph.add_node("parallel_research", parallel_research_node)
    graph.add_node("writer",            writer_node)

    graph.add_edge(START,               "parallel_research")
    graph.add_edge("parallel_research", "writer")
    graph.add_edge("writer",            END)

    return graph.compile()


def run_stratumai(company_name: str) -> str:
    graph = build_graph()

    initial_state = {
        "company_name":       company_name,
        "research_findings":  "",
        "sentiment_findings": "",
        "financial_findings": "",
        "final_report":       ""
    }

    print(f"\n🚀 StratumAI starting analysis for: {company_name}\n")
    result = graph.invoke(initial_state)
    return result["final_report"]


if __name__ == "__main__":
    company = input("Enter company name: ")
    report  = run_stratumai(company)
    print("\n" + "="*60)
    print("FINAL INTELLIGENCE BRIEF")
    print("="*60 + "\n")
    print(report)