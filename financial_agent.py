from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
import os

load_dotenv(override=True)

def run_financial_agent(company_name: str) -> str:

    llm = ChatMistralAI(
        model="mistral-small-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0
    )

    search_tool = TavilySearch(max_results=3)
    tools = [search_tool]

    agent = create_agent(llm, tools)

    query = f"""Search the web for financial and business signals about '{company_name}'.

    Specifically search for:
    - Recent funding rounds or investments
      (search: "{company_name} funding round 2025")
    - Valuation changes or IPO news
      (search: "{company_name} valuation IPO 2025")
    - What roles they are actively hiring for
      (search: "{company_name} hiring jobs 2025")
    - Revenue or growth numbers if publicly available
      (search: "{company_name} revenue growth 2025")
    - Any cost cutting, layoffs, or restructuring
      (search: "{company_name} layoffs restructuring 2025")

    Summarize findings under these exact headings:
    - FUNDING & VALUATION
    - HIRING SIGNALS (what they are building based on who they are hiring)
    - REVENUE & GROWTH
    - RISKS & RESTRUCTURING
    - STRATEGIC OUTLOOK (your interpretation of where this company is headed)"""

    result = agent.invoke({
        "messages": [HumanMessage(content=query)]
    })

    return result["messages"][-1].content


if __name__ == "__main__":
    company = input("Enter company name for financial analysis: ")
    print("\n--- FINANCIAL FINDINGS ---\n")
    findings = run_financial_agent(company)
    print(findings)