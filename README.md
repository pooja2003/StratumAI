# 🧠 StratumAI — Multi-Agent Competitive Intelligence System

<div align="center">

![StratumAI Banner](https://img.shields.io/badge/StratumAI-Multi--Agent%20Intelligence-4FACFE?style=for-the-badge&logo=robot&logoColor=white)

[![Live Demo](https://img.shields.io/badge/Live%20Demo-stratumai.streamlit.app-00F2FE?style=for-the-badge&logo=streamlit&logoColor=white)](https://stratumai.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-7F00FF?style=for-the-badge)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-E100FF?style=for-the-badge&logo=streamlit)](https://streamlit.io)

**An autonomous AI system that deploys three specialized agents in parallel to research companies, analyze public sentiment, and track financial signals — then synthesizes everything into a professional intelligence brief.**

[Live Demo](https://stratumai.streamlit.app/) · [Report a Bug](https://github.com/pooja2003/StratumAI/issues) · [Request a Feature](https://github.com/pooja2003/StratumAI/issues)

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Live Demo](#-live-demo)
- [Local Setup](#-local-setup)
- [Environment Variables](#-environment-variables)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Troubleshooting](#-troubleshooting)

---

## 🔍 Overview

StratumAI is a production-grade **multi-agent competitive intelligence system** built with LangGraph. When you enter a company name, three specialized AI agents fire simultaneously — one searches for news, one analyzes public sentiment, and one tracks financial signals. A fourth Writer Agent synthesizes all findings into a structured intelligence brief, which you can download as PDF or receive via email.

Built to demonstrate real-world agentic AI architecture — parallel agent execution, shared state management, persistent caching, and automated scheduling.

---

## 🏗 Architecture

```
User Input (Company Name)
        │
        ▼
┌───────────────────────────────────────────┐
│         LangGraph StateGraph              │
│              (Orchestrator)               │
└───────────────┬───────────────────────────┘
                │ Parallel Execution (ThreadPoolExecutor)
    ┌───────────┼───────────┐
    ▼           ▼           ▼
🔍 Research  💬 Sentiment  💰 Financial
   Agent        Agent        Agent
(Web Search) (Reddit/HN)  (Funding/Jobs)
    │           │           │
    └───────────┴───────────┘
                │
                ▼
         ✍️ Writer Agent
     (Synthesizes all findings)
                │
        ┌───────┴────────┐
        ▼                ▼
  📊 Streamlit UI    📧 Email Report
  (PDF Download)    (Gmail SMTP)
        │
        ▼
  💾 Upstash Redis   🗄 Supabase
  (Report Cache)    (Scheduled Jobs)
```

---

## ✨ Features

- **Parallel Agent Execution** — Research, Sentiment, and Financial agents run simultaneously via `ThreadPoolExecutor`, cutting analysis time by ~60%
- **LangGraph State Management** — Shared `TypedDict` state passed across all agents with full lifecycle control
- **Persistent Redis Cache** — Reports cached in Upstash Redis for 6 hours.
- **Automated Weekly Scheduler** — Schedule reports for any day/time; jobs persisted in Supabase and survive app restarts
- **Email Delivery** — Full HTML email with PDF attachment sent via Gmail SMTP
- **PDF Export** — Clean formatted PDF generated with ReportLab, handles all Unicode characters
- **User-Isolated Scheduler** — Each user's jobs filtered by email — no login required
- **Real-time Progress UI** — Progress bar and status indicators update as agents complete
- **6-Section Intelligence Brief** — Executive Summary, Key Developments, Market Sentiment, Financial Signals, Strategic Implications, Watch List

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Agent Orchestration** | LangGraph, LangChain |
| **LLM** | Mistral AI (`mistral-small-latest`) |
| **Web Search** | Tavily Search API |
| **Frontend** | Streamlit |
| **PDF Generation** | ReportLab |
| **Email** | Gmail SMTP (smtplib) |
| **Cache** | Upstash Redis |
| **Database** | Supabase (PostgreSQL) |
| **Deployment** | Streamlit Community Cloud |

---

## 🌐 Live Demo

👉 **[stratumai.streamlit.app](https://stratumai.streamlit.app)**

Try searching for: `Zepto`, `Razorpay`, `Flipkart`, `Salesforce`, or any company you want.

> **Note:** First-time searches take ~60–90 seconds as 3 agents run in parallel. Subsequent searches for the same company within 6 hours return instantly from cache.

---

## 💻 Local Setup

### Prerequisites

- Python 3.10 or higher
- Git
- A Gmail account (for email features)
- API keys 

### Step 1 — Clone the Repository

```bash
git clone https://github.com/pooja2003/StratumAI.git
cd stratumai
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

Create a `.env` file in the root directory:

```env
MISTRAL_API_KEY=your_mistral_key_here
TAVILY_API_KEY=your_tavily_key_here

GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

UPSTASH_REDIS_REST_URL=https://your-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token_here

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key_here
```

### Step 5 — Set Up Supabase Table

Go to your Supabase project → **SQL Editor** → run this:

```sql
create table scheduled_jobs (
    id uuid default gen_random_uuid() primary key,
    companies text[],
    recipient text,
    day text,
    time_str text,
    created_at timestamp default now()
);
```

### Step 6 — Run the App

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` — you should see the StratumAI interface.

---

## 🔐 Environment Variables

| Variable | Description | Where to Get |
|---|---|---|
| `MISTRAL_API_KEY` | Mistral AI API key | [console.mistral.ai](https://console.mistral.ai) |
| `TAVILY_API_KEY` | Tavily web search key | [app.tavily.com](https://app.tavily.com) |
| `GMAIL_ADDRESS` | Your Gmail address | Your Gmail account |
| `GMAIL_APP_PASSWORD` | Gmail App Password (16 chars) | Google Account → Security → App Passwords |
| `UPSTASH_REDIS_REST_URL` | Upstash Redis endpoint URL | [upstash.com](https://upstash.com) |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash Redis auth token | [upstash.com](https://upstash.com) |
| `SUPABASE_URL` | Supabase project URL | Supabase → Settings → API |
| `SUPABASE_KEY` | Supabase anon/public key | Supabase → Settings → API |

---

## 📁 Project Structure

```
stratumai/
├── app.py                  # Streamlit UI — main entry point
├── graph.py                # LangGraph StateGraph — agent orchestration
├── research_agent.py       # Research Agent — web news search
├── sentiment_agent.py      # Sentiment Agent — Reddit/HN analysis
├── financial_agent.py      # Financial Agent — funding/hiring signals
├── email_sender.py         # Gmail SMTP — HTML email + PDF attachment
├── scheduler.py            # Supabase-backed persistent job scheduler
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

---

## ⚙️ How It Works

### 1. Agent Execution (graph.py)

When a company name is submitted, LangGraph initializes a `StratumAIState` TypedDict and passes it to a `parallel_research_node` which uses Python's `ThreadPoolExecutor` to run all three agents simultaneously:

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    future_research  = executor.submit(run_research_agent,  company)
    future_sentiment = executor.submit(run_sentiment_agent, company)
    future_financial = executor.submit(run_financial_agent, company)
```

All three results are written back to shared state, which the Writer Agent reads to produce the final report.

### 2. Caching (Upstash Redis)

Every report is cached using the company name as a key (lowercased and stripped):

```
report:swiggy  →  "## 1. Executive Summary..."  (TTL: 6 hours)
```

`Swiggy`, `SWIGGY`, and `swiggy` all resolve to the same cache key. Cache is shared across all users since company data is not personal — this reduces API costs and improves response time for everyone.

### 3. Scheduler (Supabase)

Jobs are stored in a Supabase PostgreSQL table and reloaded on every app startup. A background thread runs `schedule.run_pending()` every 60 seconds. Users access only their own jobs by entering their email as a soft identifier.

### 4. Email Delivery (Gmail SMTP)

Reports are converted to styled HTML and a formatted PDF (via ReportLab) is attached. Sent via Gmail SMTP on port 587 with STARTTLS — works on both local and cloud environments.

---

## 🙋 Troubleshooting

**`ModuleNotFoundError` on startup**
```bash
pip install -r requirements.txt
```

**`(venv)` not showing in terminal**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**Redis connection error**
- Double-check `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` in your `.env`
- Make sure there are no extra spaces or quotes around the values

**Email not sending**
- Confirm 2-Step Verification is enabled on your Google account
- Make sure you generated an **App Password**, not using your regular Gmail password
- Verify `email_sender.py` uses port `587` with `smtplib.SMTP` (not `SMTP_SSL`)

**Agents returning no results / "unfortunately I could not find..."**
- Check your `TAVILY_API_KEY` is valid at [app.tavily.com](https://app.tavily.com)
- Check your `MISTRAL_API_KEY` is valid at [console.mistral.ai](https://console.mistral.ai)
- Try reducing `max_results=3` in your agent files if hitting rate limits

**Scheduler jobs not appearing after restart**
- Confirm the Supabase table was created using the SQL in [Step 5](#step-5--set-up-supabase-table)
- Check `SUPABASE_URL` and `SUPABASE_KEY` are correct in `.env`

---

## 👩‍💻 Author

**Pooja Tumma** — Software Engineer | AI/ML Enthusiast

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Pooja%20Tumma-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/pooja-tumma)
[![Email](https://img.shields.io/badge/Email-poojagtumma%40gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:poojagtumma@gmail.com)

---

<div align="center">

**Built with LangGraph · LangChain · Mistral AI · Tavily · Streamlit · Supabase · Upstash Redis**

⭐ If you found this useful, please star the repo — it helps others discover it!

</div>