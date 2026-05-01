from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
import os

load_dotenv(override=True) 

# print("Mistral key loaded:", os.getenv("MISTRAL_API_KEY") is not None)
# print("Tavily key loaded:", os.getenv("TAVILY_API_KEY") is not None)

def run_research_agent(company_name: str) -> str:    

    # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-2.0-flash",
    #     google_api_key=os.getenv("GEMINI_API_KEY"),
    #     temperature=0
    # )
    llm = ChatMistralAI(
        model="mistral-small-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0
    )

    search_tool = TavilySearch(max_results=5)
    tools = [search_tool]

    agent = create_agent(llm, tools)

    query = f"""Research the company '{company_name}' and find:
    - Recent product launches or updates
    - Partnerships or acquisitions
    - Leadership changes
    - Market expansion or new customers
    - Any controversies or challenges

    Be specific with dates, numbers and names where available.
    Summarize findings in clear bullet points."""

    result = agent.invoke({
        "messages": [HumanMessage(content=query)]
    })

    return result["messages"][-1].content


if __name__ == "__main__":
    company = input("Enter company name to research: ")
    print("\n--- RESEARCH FINDINGS ---\n")
    findings = run_research_agent(company)
    print(findings)