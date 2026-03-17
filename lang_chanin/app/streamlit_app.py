import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text

from agent.tools.db import engine
from agent.agent import run_agent

# ── SAYFA AYARLARI ───────────────────────────────────────
st.set_page_config(
    page_title="B2B Sales Analytics Copilot",
    page_icon="📊",
    layout="wide"
)

st.title("📊 B2B Sales Analytics Copilot")
st.markdown("Satış verinize doğal dilde soru sorun — AI analiz etsin.")
st.divider()

# ── KPI KARTLARI ─────────────────────────────────────────
st.markdown("### 📊 Genel Bakış")

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
    k1.metric(label="💰 Toplam Pipeline",   value=f"${pipeline/1_000_000:.1f}M")
    k2.metric(label="🎯 Ortalama Win Rate", value=f"%{win_rate}")
    k3.metric(label="📈 Toplam Gelir",      value=f"${revenue/1_000_000:.1f}M")
    k4.metric(label="🔄 Aktif Deals",       value=f"{int(active_deals)}")

except Exception as e:
    st.warning(f"KPI verileri yüklenemedi: {str(e)}")

st.divider()

# ── SOL PANEL ────────────────────────────────────────────
with st.sidebar:
    st.header("💡 Örnek Sorular")
    examples = [
        "En yüksek win rate'e sahip sektör hangisi?",
        "En iyi performans gösteren satışçı kim?",
        "Gelirde anomali var mı?",
        "Hangi aşamada en fazla deal var?",
        "Technology sektöründeki dealların ortalama değeri nedir?",
        "Win rate en düşük sektör hangisi ve neden?",
        "Aylık gelir trendi nasıl?",
        "Satış hunisinde hangi aşamada en fazla deal var?",
    ]
    for example in examples:
        if st.button(example, use_container_width=True):
            st.session_state.selected_question = example
    st.divider()
    st.markdown("**Stack:** PostgreSQL · dbt · LangChain · Groq")

# ── SORU ALANI ───────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    question = st.text_input(
        "Sorunuzu yazın:",
        value=st.session_state.get("selected_question", ""),
        placeholder="Örn: En iyi satışçı kim?",
        key="question_input"
    )
    ask_button = st.button("🔍 Analiz Et", type="primary", use_container_width=True)

with col2:
    st.markdown("### Nasıl Çalışır?")
    st.markdown("""
    1. Soru yazın
    2. Agent soruyu sınıflandırır
    3. SQL çalıştırır / Anomali arar
    4. AI sonucu yorumlar
    """)

st.divider()

# ── CEVAP ALANI ──────────────────────────────────────────
if ask_button and question:
    with st.spinner("Analiz ediliyor..."):
        try:
            response = run_agent(question)
            st.markdown("### 📈 Analiz Sonucu")
            st.success(response)

            q = question.lower()
            with engine.connect() as conn:
                if any(w in q for w in ["satışçı", "temsilci", "sales rep", "performans"]):
                    df = pd.read_sql(text("SELECT sales_rep, total_won_revenue, win_rate_pct FROM raw.sales_rep_performance ORDER BY total_won_revenue DESC LIMIT 10"), conn)
                    fig = px.bar(df, x="sales_rep", y="total_won_revenue", title="Top 10 Satışçı", color="win_rate_pct", color_continuous_scale="Blues")
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ["sektör", "industry", "segment"]):
                    df = pd.read_sql(text("SELECT industry, total_pipeline_value, won_revenue FROM raw.pipeline_by_industry ORDER BY total_pipeline_value DESC"), conn)
                    fig = px.bar(df, x="industry", y=["total_pipeline_value", "won_revenue"], title="Sektör Bazında Pipeline", barmode="group")
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ["anomali", "gelir", "revenue", "trend", "aylık"]):
                    df = pd.read_sql(text("SELECT revenue_month, total_revenue, revenue_type FROM raw.monthly_revenue ORDER BY revenue_month"), conn)
                    fig = px.line(df, x="revenue_month", y="total_revenue", color="revenue_type", title="Aylık Gelir Trendi")
                    st.plotly_chart(fig, use_container_width=True)

                elif any(w in q for w in ["funnel", "aşama", "huni", "stage"]):
                    df = pd.read_sql(text("SELECT stage, deal_count FROM raw.deal_funnel ORDER BY CASE stage WHEN 'Prospecting' THEN 1 WHEN 'Qualification' THEN 2 WHEN 'Proposal' THEN 3 WHEN 'Negotiation' THEN 4 WHEN 'Closed Won' THEN 5 WHEN 'Closed Lost' THEN 6 END"), conn)
                    fig = px.funnel(df, x="deal_count", y="stage", title="Satış Hunisi")
                    st.plotly_chart(fig, use_container_width=True)

            if "history" not in st.session_state:
                st.session_state.history = []
            st.session_state.history.append({"question": question, "answer": response})

        except Exception as e:
            st.error("Bir hata oluştu, soruyu farklı sormayı deneyin.")

elif ask_button and not question:
    st.warning("Lütfen bir soru yazın.")

# ── GEÇMİŞ ───────────────────────────────────────────────
if "history" in st.session_state and st.session_state.history:
    st.divider()
    st.markdown("### 🕒 Önceki Sorular")
    for item in reversed(st.session_state.history[-5:]):
        with st.expander(f"❓ {item['question']}"):
            st.write(item["answer"])