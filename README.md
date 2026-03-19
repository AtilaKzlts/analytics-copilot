<div align="center">
  <h1>AI-Powered Analytics Copilot</h1>
 </p>
</div>

![image](https://github.com/AtilaKzlts/analytics-copilot/blob/main/pics/Screenshot_1.png)

> **Your data analyst in seconds.** Just ask a question. Get insights instantly. No SQL, no waiting, no spreadsheets.



## The Problem This Solves

**Today's workflow:**
- Sales team asks: "Why did we lose deals last month?"
- You spend 30 minutes writing SQL queries
- You spend another 30 minutes interpreting data in Excel
- You write a summary report
- **Total time: 2-3 hours**

**With this system:**
- Sales team asks: "Why did we lose deals last month?"
- System understands the question, pulls the data, spots the patterns, and gives you the answer
- **Total time: 5 seconds** ✓

---

## Why This Project Matters

### 1. **It Thinks, Not Just Automates**
- It understands what you're asking for
- It knows when to look at raw numbers vs. spotting unusual patterns
- It explains findings in business language, not data science jargon

### 2. **Works for Any Business (Truly)**
Switch from E-commerce to SaaS to Finance? Just change one config file. The whole system adapts. No code changes needed.

### 3. **Catches the Red Flags**
Automatically detects when something unusual is happening in your numbers — before anyone notices.


## What It Does

| Your Question | System Does | You Get |
|---|---|---|
| "Who's our best salesperson?" | Pulls sales data, calculates win rates | Clear answer + visualization |
| "Is revenue behaving normally?" | Scans for unusual patterns | Alert if something's off |
| "Why did we miss targets?" | Combines data + analysis | Full explanation + why it happened |



## How It Works (Simple Version)

```
You ask a question (in plain English)
            ↓
AI understands what you need
            ↓
System pulls the right data
            ↓
Spots patterns & anomalies  
            ↓
AI explains findings in business language
            ↓
You get insights (not raw data)
```

---

## What Powers It

- **Smart AI** (Claude/Groq) — Understands questions and writes explanations
- **Database** (PostgreSQL) — Stores and organizes your data
- **Analytics Pipeline** (dbt) — Cleans and prepares data automatically
- **Dashboard** (Streamlit) — Clean, modern interface


## Real Examples

✅ **"Who's our top-performing salesperson?"**  
→ System pulls sales data, calculates metrics → You get ranking + insights

✅ **"Is there something odd about this month's revenue?"**  
→ System scans for unusual patterns → You get alerts with explanations

✅ **"Why are we losing deals in this pipeline stage?"**  
→ System analyzes data + spots trends → You get full analysis + recommendations

---

## Quick Start

### Option 1: Try the Demo (No Setup)
Live version: [analytics-copilot.streamlit.app](https://analytics-copilot.streamlit.app)

Just click and ask questions.

### Option 2: Run Locally
```bash
git clone https://github.com/yourusername/analytics-copilot
cd analytics-copilot
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Then open `http://localhost:8501` in your browser.

---

## What You'll See

- **Clean Dashboard** — Everything at a glance
- **Smart Charts** — Data visualized automatically
- **AI Explanations** — Not just numbers, actual insights
- **Answer Box** — Plain English answers to your questions



## Who Should Care?

- **CFO/Finance Teams** — Instant financial insights, no waiting for reports
- **Sales Leaders** — Understand pipeline, rep performance, deal patterns instantly
- **Product Teams** — See user behavior trends and anomalies
- **Data Teams** — Reduce the "ad-hoc query" burden by 80%


