# Logistics AI Agent

Natural-language querying of logistics data — built with **Python, LangChain, Groq, SQLite, and FastAPI**.

Ask plain-English questions like:

> *"Which city had the most delayed orders last week?"*
> *"What is the cancellation rate for each delivery partner?"*
> *"Compare average delivery time across North vs South zone"*

The agent converts your question → SQL → runs it → returns a formatted answer.

---

## Architecture

```
User question
     │
     ▼
FastAPI (main.py)
     │
     ▼
LangChain SQL Agent (agent.py)
 ├── ChatGroq  (Llama 3.3-70B, free tier)   ← generates SQL
 └── SQLDatabase  (SQLite)                   ← executes SQL
     │
     ▼
Formatted plain-English answer
```

### Database schema (5 000 fake orders)

| Table | Rows | Key columns |
|---|---|---|
| `orders` | 5 000 | order_id, origin_city, destination_city, delivery_partner, status, created_at, delay_reason |
| `delivery_partners` | 10 | name, base_city, rating, active_orders |
| `cities` | 15 | name, state, zone (North/South/East/West/Central) |
| `daily_metrics` | 450 | date, city, total_orders, delivered, cancelled, delayed, avg_delivery_time_hrs |

---

## Setup (5 steps)

### 1. Clone / create project folder

```bash
cd ~
mkdir logistics-agent && cd logistics-agent
# copy all project files here
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get your free Groq API key

1. Go to **https://console.groq.com**
2. Sign up (free, no credit card)
3. Click **API Keys → Create API Key**
4. Copy the key

```bash
cp .env.example .env
# open .env and paste your key:
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

### 5. Run the server

```bash
python main.py
```

Open **http://localhost:8000** in your browser.

The database is created automatically on first run (takes ~3 seconds).

---

## Test it works

```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Which city had the most delayed orders?"}'
```

---

## Project structure

```
logistics-agent/
├── main.py           # FastAPI app — routes, startup logic
├── agent.py          # LangChain SQL Agent + Groq setup
├── database.py       # SQLite creation + fake data seeding
├── index.html        # Chat UI (served by FastAPI)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Sample questions to try

- Which city had the most delayed orders in the last 30 days?
- What is the cancellation rate for each delivery partner?
- Which delivery partner has the best on-time delivery rate?
- How many orders are currently pending or in transit?
- What is the average delivery time by zone?
- Which product category gets delayed the most?
- Show me the top 5 routes with the highest delay rates
- What percentage of orders were delivered on time last week?
- Which partner has the highest number of returned orders?
- Compare total revenue by city for the last 30 days

---

## Stack

| Component | Technology | Why |
|---|---|---|
| API | FastAPI | Fast, async, auto-docs at /docs |
| Agent framework | LangChain | SQL Agent built-in, well-documented |
| LLM | Groq (Llama 3.3-70B) | Free tier, 14 400 req/day, very fast |
| Database | SQLite | Zero-setup, file-based |
| Frontend | Vanilla HTML/CSS/JS | No build step needed |
