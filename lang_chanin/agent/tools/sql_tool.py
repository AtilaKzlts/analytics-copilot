import os
from sqlalchemy import  text
from langchain.tools import tool
from pathlib import Path
from agent.tools.db import engine
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")


SCHEMA_INFO = """
Kullanılabilir tablolar (raw schema):

1. sales_rep_performance
   - sales_rep, total_deals, total_pipeline, total_won_revenue
   - won_deals, lost_deals, avg_days_to_close, win_rate_pct

2. pipeline_by_industry
   - industry, size_segment, total_deals, total_pipeline_value
   - won_revenue, won_deals, lost_deals, win_rate_pct
   - avg_deal_value, avg_days_to_close

3. deal_funnel
   - stage, deal_count, total_value, avg_deal_value
   - avg_probability, weighted_value

4. monthly_revenue
   - revenue_month, revenue_type, active_companies
   - active_deals, total_revenue, avg_revenue_per_deal
   - prev_month_revenue, mom_growth_pct

5. stg_deals
   - deal_id, company_id, deal_name, stage, deal_value
   - probability, size_segment, owner, created_date
   - closed_date, days_to_close, is_won

6. stg_companies
   - company_id, company_name, industry, size_segment, country
"""

@tool
def sql_query_tool(question: str) -> str:
    """
    Kullanıcının sorusunu SQL'e çevirip PostgreSQL'de çalıştırır.
    B2B satış pipeline verisi üzerinde sorgu yapmak için kullan.
    """
    from langchain_groq import ChatGroq
    from langchain_core.prompts import ChatPromptTemplate

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    prompt = ChatPromptTemplate.from_template("""
Sen bir SQL uzmanısın. Aşağıdaki tablo şemasına göre soruyu yanıtlayan PostgreSQL SQL sorgusu yaz.

ŞEMA:
{schema}

KURALLAR:
- Sadece SQL yaz, başka hiçbir şey yazma
- Schema adı "raw" kullan (örn: raw.sales_rep_performance)
- Maksimum 20 satır döndür
- Türkçe soru gelse de SQL İngilizce olsun

SORU: {question}

SQL:
""")

    chain = prompt | llm
    sql = chain.invoke({
        "schema": SCHEMA_INFO,
        "question": question
    }).content.strip()

    sql = sql.replace("```sql", "").replace("```", "").strip()

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())

            if not rows:
                return "Sorgu sonuç döndürmedi."

            output = " | ".join(columns) + "\n"
            output += "-" * 60 + "\n"
            for row in rows:
                output += " | ".join(str(v) for v in row) + "\n"

            return f"SQL:\n{sql}\n\nSONUÇ:\n{output}"

    except Exception as e:
        return f"SQL hatası: {str(e)}\nSQL: {sql}"