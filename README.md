<p align="center">
  <h1 align="center">⚕ AI-First CRM — HCP Interaction Module</h1>
  <p align="center">
    <strong>An intelligent CRM for pharmaceutical field reps, powered by LangGraph + LLM</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white" />
    <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" />
    <img src="https://img.shields.io/badge/LangGraph-Agent-FF6F00?logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/Groq-LLM-8B5CF6?logo=groq&logoColor=white" />
    <img src="https://img.shields.io/badge/PostgreSQL-DB-4169E1?logo=postgresql&logoColor=white" />
    <img src="https://img.shields.io/badge/Redux_Toolkit-State-764ABC?logo=redux&logoColor=white" />
  </p>
</p>

---

## 📋 Overview

This project implements an **AI-first Customer Relationship Management (CRM)** system specifically designed for the **Healthcare Professional (HCP)** module. Built for life science field representatives, it features a **dual-input Log Interaction Screen** where sales reps can:

1. **Chat naturally** with an AI agent to log interactions (e.g., *"Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure"*)
2. **Use a structured form** to manually enter interaction details

The AI agent, built with **LangGraph**, automatically extracts entities (HCP name, sentiment, topics, materials) from natural language, saves them to a PostgreSQL database, and **auto-fills the form in real time**.

---

## 🖥️ Screenshots

### Log Interaction — AI Chat + Auto-filled Form
> The sales rep types a natural language description of their meeting. The AI agent extracts all entities and auto-fills every form field — HCP name, attendees, topics, materials, samples, and date.

![Log HCP Interaction](Screenshots/Log-hcp-interaction.png)

### Sentiment Analysis + Outcomes + Follow-ups
> The AI correctly identifies the HCP's sentiment (Positive/Neutral/Negative), extracts outcomes, and suggests follow-up actions — all from a single chat message.

![Sentiment and Outcomes](Screenshots/sentiment-outcome.png)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React 18)                     │
│  ┌──────────────────┐  ┌──────────────────────────────────┐  │
│  │  Interaction Form │  │        AI Chat Panel             │  │
│  │  (Manual Entry)   │  │  (Natural Language → Auto-fill)  │  │
│  └────────┬─────────┘  └──────────────┬───────────────────┘  │
│           │       Redux Toolkit       │                      │
│           └───────────┬───────────────┘                      │
│                       │ Axios                                │
└───────────────────────┼──────────────────────────────────────┘
                        │ REST API
┌───────────────────────┼──────────────────────────────────────┐
│                  BACKEND (FastAPI)                            │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐    │
│  │              LangGraph AI Agent                       │    │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐               │    │
│  │  │  Tool 1  │ │  Tool 2  │ │  Tool 3  │              │    │
│  │  │   Log    │ │   Edit   │ │  Search  │              │    │
│  │  └─────────┘ └─────────┘ └──────────┘               │    │
│  │  ┌─────────────┐ ┌──────────────────────┐            │    │
│  │  │   Tool 4     │ │      Tool 5          │            │    │
│  │  │  Follow-up   │ │  Summarize History   │            │    │
│  │  └─────────────┘ └──────────────────────┘            │    │
│  └──────────────────────────────────────────────────────┘    │
│                       │                                      │
│              SQLAlchemy ORM                                  │
└───────────────────────┼──────────────────────────────────────┘
                        │
                ┌───────▼───────┐
                │  PostgreSQL   │
                │   (hcp_crm)   │
                └───────────────┘
```

---

## 🤖 LangGraph Agent — 5 Tools

The AI agent is built with **LangGraph** and uses **Groq's `llama-3.3-70b-versatile`** model for fast, intelligent tool-calling.

> **Note:** The original model `gemma2-9b-it` was [decommissioned by Groq](https://console.groq.com/docs/deprecations#october-8-2025-gemma29bit). We use `llama-3.3-70b-versatile` as recommended.

| # | Tool | Type | Description |
|---|------|------|-------------|
| 1 | `log_interaction` | **Required** | Parses natural language to extract HCP name, interaction type, topics, sentiment, materials, samples, outcomes, and follow-ups. Saves to PostgreSQL and returns form updates to auto-fill the UI. |
| 2 | `edit_interaction` | **Required** | Modifies an existing logged interaction by ID. Only updates fields that are explicitly changed (partial update). |
| 3 | `search_hcp` | Additional | Searches Healthcare Professionals by name, specialty, or institution using fuzzy matching (`ILIKE`). |
| 4 | `suggest_follow_up` | Additional | Generates intelligent follow-up recommendations based on interaction sentiment, topics discussed, and outcomes. |
| 5 | `summarize_interaction_history` | Additional | Retrieves and summarizes all past interactions with a specific HCP — sentiment trends, topic coverage, and relationship status. |

### How `log_interaction` Works (Entity Extraction Flow)

```
User: "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure"
                                    │
                         ┌──────────▼──────────┐
                         │   LLM (Groq)        │
                         │   Entity Extraction  │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │  Extracted Parameters:          │
                    │  hcp_name: "Dr. Smith"          │
                    │  interaction_type: "meeting"    │
                    │  topics: "Product X efficacy"   │
                    │  sentiment: "positive"          │
                    │  materials: "brochure"          │
                    └───────────────┬────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  PostgreSQL INSERT   │
                         │  interactions table  │
                         └──────────┬──────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  Return form_updates │
                         │  → Auto-fill UI form │
                         └─────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Redux Toolkit | UI + State Management |
| **Styling** | Vanilla CSS + Inter Font | Premium, responsive design |
| **Backend** | Python + FastAPI | REST API server |
| **AI Agent** | LangGraph + LangChain | Agentic workflow with 5 tools |
| **LLM** | Groq — `llama-3.3-70b-versatile` | Fast inference for entity extraction & tool-calling |
| **Database** | PostgreSQL + SQLAlchemy | Persistent storage with ORM |
| **HTTP Client** | Axios | Frontend-backend communication |

---

## 📁 Project Structure

```
ai-crm-hcp-module/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app + CORS + routes
│   │   ├── database.py             # SQLAlchemy engine + session
│   │   ├── models.py               # HCP & Interaction DB models
│   │   ├── schemas.py              # Pydantic validation schemas
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py             # POST /api/chat → AI agent
│   │   │   ├── interactions.py     # CRUD /api/interactions
│   │   │   └── hcps.py             # CRUD /api/hcps
│   │   └── agents/
│   │       ├── __init__.py
│   │       └── hcp_agent.py        # LangGraph agent (5 tools)
│   ├── requirements.txt
│   ├── .env                        # API keys (gitignored)
│   └── .env.example
├── frontend/
│   ├── public/index.html
│   ├── src/
│   │   ├── index.js                # React entry point
│   │   ├── App.js                  # Redux Provider wrapper
│   │   ├── api/axios.js            # Axios instance
│   │   ├── store/
│   │   │   ├── index.js            # Redux store config
│   │   │   ├── interactionSlice.js # Interaction state + async thunks
│   │   │   └── chatSlice.js        # Chat state + AI messaging
│   │   ├── components/
│   │   │   ├── InteractionForm.js  # Structured form component
│   │   │   ├── InteractionForm.css
│   │   │   ├── ChatPanel.js        # AI chat interface
│   │   │   ├── ChatPanel.css
│   │   │   ├── InteractionHistory.js # History view + edit/delete
│   │   │   └── InteractionHistory.css
│   │   ├── pages/
│   │   │   ├── LogInteractionScreen.js  # Main dashboard page
│   │   │   └── LogInteractionScreen.css
│   │   └── styles/
│   │       └── global.css          # Design tokens + Inter font
│   └── package.json
├── Screenshots/
│   ├── Log-hcp-interaction.png
│   └── sentiment-outcome.png
├── README.md
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **PostgreSQL** running locally
- **Groq API Key** → [console.groq.com](https://console.groq.com)

### 1️⃣ Database Setup

```sql
CREATE DATABASE hcp_crm;
```

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Configure environment variables:

```bash
# backend/.env
GROQ_API_KEY=gsk_your_key_here
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/hcp_crm
```

Start the server:

```bash
uvicorn app.main:app --reload
# → API running at http://localhost:8000
```

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm start
# → App running at http://localhost:3000
```

---

## 💬 Usage Examples

### Log an Interaction (via AI Chat)

```
"Today I had a meeting with Dr. Sarah Williams. Attendees were myself and nurse John. 
We discussed Cardio-X efficacy and side effects. I shared the clinical trial brochure 
and distributed 3 samples of Cardio-X. The sentiment was positive — she was very 
interested. The outcome was she agreed to prescribe Cardio-X for suitable patients. 
Follow-up: Schedule a call in 2 weeks to check on patient feedback."
```

→ The AI extracts **all fields** and auto-fills the form.

### Edit an Interaction

```
"Change the sentiment of interaction 18 to neutral and update the outcomes to 'pending decision'"
```

### Search for an HCP

```
"Search for Dr. Sarah Williams"
```

### Get Follow-up Suggestions

```
"Suggest follow-ups for Dr. Williams, positive sentiment, discussed efficacy"
```

### Summarize Interaction History

```
"Summarize interaction history with Dr. Williams"
```

---

## ✨ Key Features

- **🤖 AI-First Approach** — Natural language interaction logging powered by LangGraph + Groq
- **📝 Dual Input** — Log via AI chat OR structured form (both sync to the same state)
- **🔄 Auto-Fill** — AI chat responses automatically populate form fields via Redux
- **😊😐😞 Sentiment Tracking** — Visual sentiment badges with positive/neutral/negative classification
- **📊 Interaction History** — Full CRUD with edit and delete capabilities
- **💡 Smart Follow-ups** — Context-aware follow-up recommendations based on sentiment and topics
- **📋 History Summaries** — AI-generated relationship overviews with sentiment trends
- **📱 Responsive Design** — Works on desktop and mobile with Inter font and modern UI

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/` | Send message to AI agent |
| `GET` | `/api/interactions/` | List all interactions |
| `POST` | `/api/interactions/` | Create interaction (manual) |
| `PUT` | `/api/interactions/{id}` | Update interaction |
| `DELETE` | `/api/interactions/{id}` | Delete interaction |
| `GET` | `/api/hcps/` | List/search HCPs |
| `POST` | `/api/hcps/` | Create HCP |

---

## 📄 License

MIT
