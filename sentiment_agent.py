from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
import os

load_dotenv(override=True)

def run_sentiment_agent(company_name: str) -> str:

    llm = ChatMistralAI(
        model="mistral-small-latest",
        api_key=os.getenv("MISTRAL_API_KEY"),
        temperature=0
    )

    search_tool = TavilySearch(max_results=3)
    tools = [search_tool]

    agent = create_agent(llm, tools)

    query = f"""Search the web for public opinion and sentiment about '{company_name}'.

    Specifically search for:
    - Reddit discussions mentioning {company_name} (search: "{company_name} site:reddit.com")
    - Developer or user complaints and praise
    - Employee sentiment (search: "{company_name} employees glassdoor reviews 2025")
    - Social media buzz or trending topics about this company
    - Customer reviews or feedback patterns

    Summarize the overall public sentiment as:
    - POSITIVE points (what people love)
    - NEGATIVE points (what people complain about)
    - OVERALL sentiment score: Positive / Neutral / Negative"""

    result = agent.invoke({
        "messages": [HumanMessage(content=query)]
    })

    return result["messages"][-1].content


if __name__ == "__main__":
    company = input("Enter company name for sentiment analysis: ")
    print("\n--- SENTIMENT FINDINGS ---\n")
    findings = run_sentiment_agent(company)
    print(findings)