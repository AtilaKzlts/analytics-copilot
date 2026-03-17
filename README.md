# B2B Sales Analytics Copilot

> An AI-powered analytics agent that answers natural language questions about sales data — it writes SQL, detects anomalies, and generates business insights automatically.

**🔗 [Live Demo](https://analytics-copilot-ypywezydn7u3ear2uvgdor.streamlit.app/)**

---

## What It Does

Most analytics workflows look like this: someone asks a question → analyst writes SQL → pulls data → interprets it → writes a summary. That takes hours.

This project compresses that into seconds.

You type *"Which industry has the lowest win rate and why?"* — the agent figures out what tools to use, runs the right queries, detects any statistical anomalies, and returns a plain-language business interpretation.

```
User: "Why did revenue drop last month?"

Agent:
  → Classifies question as ANOMALY
  → Runs Z-score analysis on monthly_revenue
  → Detects 2 outlier months (z > 2.0)
  → Sends findings to insight tool
  → Returns: plain-language explanation + 3 actionable recommendations
```

---

## Architecture

```
User Question (natural language)
        │
        ▼
 LangChain Agent  ──── classifies intent ────▶  SQL / ANOMALY / BOTH
        │
        ├──▶ [Tool 1] sql_tool.py
        │      Text → SQL → PostgreSQL → result table
        │
        ├──▶ [Tool 2] anomaly_tool.py
        │      Z-score analysis → statistical alerts
        │
        └──▶ [Tool 3] insight_tool.py
               LLM → business interpretation + recommendations
                        │
                        ▼
              Streamlit UI  (KPI cards + charts + AI response)
```

**Data layer:** Raw CRM data → dbt staging models → dbt mart models → PostgreSQL

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Database | PostgreSQL | Stores transformed sales data |
| Transformation | dbt | Raw → staging → mart models |
| AI Agent | LangChain + Groq (LLaMA 3.3 70B) | Natural language → SQL + reasoning |
| Anomaly Detection | Python (Z-score) | Statistical outlier detection |
| UI | Streamlit + Plotly | Interactive dashboard |

---

## Data

Anonymized B2B sales CRM data covering:

- **300+ deals** across 6 pipeline stages (Prospecting → Closed Won/Lost)
- **Companies** spanning 8 industries, 3 segments (SMB / Mid-Market / Enterprise), multiple countries
- **Sales rep performance** — win rates, average deal size, days to close
- **Monthly revenue** — Recurring vs. One-time, MoM growth tracking

dbt transforms raw tables into four mart models used by the agent:

```
stg_deals / stg_companies / stg_contacts / stg_revenues / stg_activities
        ↓
deal_funnel · monthly_revenue · pipeline_by_industry · sales_rep_performance
```

---

## Agent Logic

The agent does **not** follow a fixed script. It classifies the question first, then decides which tools to invoke:

```python
# From agent.py
classification = llm.invoke(classify_prompt)  # → SQL, ANOMALY, or BOTH

if "ANOMALY" in classification:
    metric = llm.invoke(metric_prompt)         # → revenue / win_rate / deals / ...
    result = anomaly_tool.invoke(metric)
else:
    result = sql_query_tool.invoke(question)

insight = insight_tool.invoke(result)          # always runs
```

The anomaly tool uses Z-score (threshold: ±2σ) to flag outliers in any metric. The insight tool always runs last — it takes raw results and produces the final business-readable response.

---

## Example Questions

These all work on the live demo:

- *"Which sales rep has the highest win rate?"*
- *"Is there an anomaly in monthly revenue?"*
- *"Which industry has the most pipeline value?"*
- *"Where in the funnel are we losing the most deals?"*
- *"What's the average deal size for Enterprise segment?"*

---

## Local Setup

```bash
git clone https://github.com/AtilaKzlts/analytics-copilot
cd analytics-copilot

pip install -r requirements.txt
```

Create a `.env` file in `lang_chanin/`:

```env
GROQ_API_KEY=your_groq_api_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=analytics_copilot
DB_USER=your_user
DB_PASSWORD=your_password
```

Load data and run dbt:

```bash
cd lang_chanin
python load_data.py
cd analytics_copilot
dbt run
```

Launch the app:

```bash
streamlit run lang_chanin/app/streamlit_app.py
```

---


*Data has been anonymized. All company names and personal identifiers are synthetic.*
