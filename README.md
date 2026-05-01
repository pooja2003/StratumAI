# 🧠 StratumAI — Multi-Agent Competitive Intelligence System

Multi-agent AI system that researches companies in parallel and
delivers weekly intelligence briefs to your inbox.

## Architecture
- **Research Agent** — finds latest news and developments
- **Sentiment Agent** — analyzes public and employee sentiment
- **Financial Agent** — tracks funding, hiring, and growth signals
- **Writer Agent** — synthesizes everything into a structured brief

## Tech Stack
LangGraph · LangChain · Mistral AI · Tavily Search · Streamlit · ReportLab

## Features
- Parallel agent execution via LangGraph StateGraph
- Streamlit web UI with real-time agent status
- PDF + Markdown report export
- Automated weekly email delivery via Gmail SMTP
- Configurable company watchlist

## Setup
pip install -r requirements.txt
Add your API keys to .env
streamlit run app.py
