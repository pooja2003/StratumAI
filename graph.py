from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from research_agent import run_research_agent
from sentiment_agent import run_sentiment_agent
from financial_agent import run_financial_agent
import os

load_dotenv(override=True)

# ─────────────────────────────────────────
# SHARED STATE
# This is the "shared notepad" all agents
# read from and write to
# ─────────────────────────────────────────
class StratumAIState(TypedDict):
    company_name: str
    research_findings: str
    sentiment_findings: str
    financial_findings: str
    final_report: str


# ─────────────────────────────────────────
# AGENT NODES
# Each function is one node in the graph
# ─────────────────────────────────────────
def research_node(state: StratumAIState) -> StratumAIState:
    print("🔍 Research Agent running...")
    findings = run_research_agent(state["company_name"])
    return {"research_findings": findings}

def sentiment_node(state: StratumAIState) -> StratumAIState:
    print("💬 Sentiment Agent running...")
    findings = run_sentiment_agent(state["company_name"])
    return {"sentiment_findings": findings}

def financial_node(state: StratumAIState) -> StratumAIState:
    print("💰 Financial Agent running...")
    findings = run_financial_agent(state["company_name"])
    return {"financial_findings": findings}

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

Now write a professional Competitive Intelligence Brief with these
exact sections:

# {state["company_name"]} — Intelligence Brief

## 1. Executive Summary
(3-4 sentences summarizing the most important things to know)

## 2. Key Developments
(Recent news and product updates that matter)

## 3. Market Sentiment
(What customers, employees and the public think)

## 4. Financial & Growth Signals
(Funding, hiring trends, revenue signals)

## 5. Strategic Implications
(What this all means — where is this company headed?)

## 6. Watch List
(3 specific things to monitor about this company in the next 90 days)

Be concise, specific, and use bullet points inside each section."""

    response = llm.invoke([HumanMessage(content=prompt)])
    return {"final_report": response.content}


# ─────────────────────────────────────────
# BUILD THE GRAPH
# ─────────────────────────────────────────
def build_graph():
    graph = StateGraph(StratumAIState)

    # Add all four nodes
    graph.add_node("research", research_node)
    graph.add_node("sentiment", sentiment_node)
    graph.add_node("financial", financial_node)
    graph.add_node("writer", writer_node)

    # All three agents start at the same time (parallel execution)
    graph.add_edge(START, "research")
    graph.add_edge(START, "sentiment")
    graph.add_edge(START, "financial")

    # All three feed into the writer when done
    graph.add_edge("research", "writer")
    graph.add_edge("sentiment", "writer")
    graph.add_edge("financial", "writer")

    # Writer produces the final output
    graph.add_edge("writer", END)

    return graph.compile()


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
def run_stratumai(company_name: str) -> str:
    graph = build_graph()

    initial_state = {
        "company_name": company_name,
        "research_findings": "",
        "sentiment_findings": "",
        "financial_findings": "",
        "final_report": ""
    }

    print(f"\n🚀 StratumAI starting analysis for: {company_name}\n")
    result = graph.invoke(initial_state)
    return result["final_report"]


if __name__ == "__main__":
    company = input("Enter company name: ")
    report = run_stratumai(company)
    print("\n" + "="*60)
    print("FINAL INTELLIGENCE BRIEF")
    print("="*60 + "\n")
    print(report)