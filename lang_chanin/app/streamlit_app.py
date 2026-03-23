import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from agent.tools.db import engine
from agent.agent import run_agent

# ── PAGE CONFIG ──────────────────────────────────────────
st.set_page_config(
    page_title="B2B Sales Analytics Copilot",
    page_icon="📊",
    layout="wide"
)

st.title("📊 B2B Sales Analytics Copilot")
st.markdown("Ask anything about your sales pipeline — the agent handles the rest.")
st.divider()

# ── KPI CARDS ────────────────────────────────────────────
st.markdown("### Overview")

try:
    with engine.connect() as conn:
        pipeline = pd.read_sql(
            text("SELECT SUM(total_pipeline_value) as total FROM raw.pipeline_by_industry"), conn
        ).iloc[0]["total"]
        win_rate = pd.read_sql(
            text("SELECT ROUND(AVG(win_rate_pct)::numeric, 1) as avg FROM raw.pipeline_by_industry"), conn
        ).iloc[0]["avg"]
        revenue = pd.read_sql(
            text("SELECT SUM(total_revenue) as total FROM raw.monthly_revenue"), conn
        ).iloc[0]["total"]
        active_deals = pd.read_sql(
            text("SELECT SUM(deal_count) as total FROM raw.deal_funnel WHERE stage NOT IN ('Closed Won', 'Closed Lost')"), conn
        ).iloc[0]["total"]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(label="💰 Total Pipeline",  value=f"${pipeline/1_000_000:.1f}M")
    k2.metric(label="🎯 Avg Win Rate",    value=f"{win_rate}%")
    k3.metric(label="📈 Total Revenue",   value=f"${revenue/1_000_000:.1f}M")
    k4.metric(label="🔄 Active Deals",    value=f"{int(active_deals)}")

except Exception as e:
    st.warning(f"Could not load KPI data: {str(e)}")

st.divider()

# ── SIDEBAR ──────────────────────────────────────────────
with st.sidebar:
    st.header("💡 Example Questions")
    st.markdown("Click to load:")

    examples = [
        "Which industry has the highest win rate?",
        "Who is the top performing sales rep?",
        "Are there any anomalies in revenue?",
        "Which pipeline stage has the most deals?",
        "What is the average deal value in the Technology sector?",
        "Which industry has the lowest win rate and why?",
        "Show me the monthly revenue trend",
        "Break down the sales funnel by stage",
    ]

    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.selected_question = example

    st.divider()
    st.markdown("**Stack:** PostgreSQL · dbt · LangChain · Groq")

# ── QUESTION INPUT ───────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    question = st.text_input(
        "Ask a question:",
        value=st.session_state.get("selected_question", ""),
        placeholder="e.g. Who closed the most deals last quarter?",
        key="question_input"
    )
    ask_button = st.button("🔍 Analyze", type="primary", use_container_width=True)

with col2:
    st.markdown("### How it works")
    st.markdown("""
    1. Type your question
    2. Agent classifies intent
    3. Runs SQL or anomaly check
    4. AI interprets the result
    """)

st.divider()

# ── ANSWER ───────────────────────────────────────────────
if ask_button and question:
    with st.spinner("Analyzing..."):
        try:
            response = run_agent(question)
            st.markdown("### 📈 Analysis")
            st.success(response)

            q = question.lower()
            with engine.connect() as conn:

                if any(w in q for w in ["sales rep", "representative", "performer", "performance", "salesperson"]):
                    df = pd.read_sql(text("""
                        SELECT sales_rep, total_won_revenue, win_rate_pct, total_deals
                        FROM raw.sales_rep_performance
                        ORDER BY total_won_revenue DESC LIMIT 10
                    """), conn)
                    fig = px.bar(
                        df, x="sales_rep", y="total_won_revenue",
                        title="Top 10 Sales Reps — Won Revenue",
                        labels={"sales_rep": "Sales Rep", "total_won_revenue": "Won Revenue ($)"},
                        color="win_rate_pct", color_continuous_scale="Blues"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ["sector", "industry", "segment"]):
                    df = pd.read_sql(text("""
                        SELECT industry, total_pipeline_value, won_revenue
                        FROM raw.pipeline_by_industry
                        ORDER BY total_pipeline_value DESC
                    """), conn)
                    fig = px.bar(
                        df, x="industry", y=["total_pipeline_value", "won_revenue"],
                        title="Pipeline & Won Revenue by Industry",
                        labels={"industry": "Industry", "value": "Value ($)"},
                        barmode="group"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ["anomaly", "revenue", "trend", "monthly", "spike"]):
                    df = pd.read_sql(text("""
                        SELECT revenue_month, total_revenue, revenue_type
                        FROM raw.monthly_revenue ORDER BY revenue_month
                    """), conn)
                    fig = px.line(
                        df, x="revenue_month", y="total_revenue",
                        color="revenue_type", title="Monthly Revenue Trend",
                        labels={"revenue_month": "Month", "total_revenue": "Revenue ($)"}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ["funnel", "stage", "pipeline breakdown"]):
                    df = pd.read_sql(text("""
                        SELECT stage, deal_count FROM raw.deal_funnel
                        ORDER BY CASE stage
                            WHEN 'Prospecting'   THEN 1
                            WHEN 'Qualification' THEN 2
                            WHEN 'Proposal'      THEN 3
                            WHEN 'Negotiation'   THEN 4
                            WHEN 'Closed Won'    THEN 5
                            WHEN 'Closed Lost'   THEN 6
                        END
                    """), conn)
                    fig = px.funnel(df, x="deal_count", y="stage", title="Sales Funnel")
                    st.plotly_chart(fig, use_container_width=True)

            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({"question": question, "answer": response})

        except Exception as e:
            st.error("Something went wrong — try rephrasing your question.")

elif ask_button and not question:
    st.warning("Please enter a question.")

# ── HISTORY ──────────────────────────────────────────────
if "history" in st.session_state and st.session_state.history:
    st.divider()
    st.markdown("### 🕒 Recent Questions")
    for item in reversed(st.session_state.history[-5:]):
        with st.expander(f"❓ {item['question']}"):
            st.write(item["answer"])