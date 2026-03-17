from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from pathlib import Path

from agent.tools.sql_tool import sql_query_tool
from agent.tools.anomaly_tool import anomaly_tool
from agent.tools.insight_tool import insight_tool

load_dotenv(Path(__file__).parent.parent / ".env")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def run_agent(question: str, chat_history: list = []) -> str:
    
    # 1. soruyu sınıflandır
    classify_prompt = f"""
Aşağıdaki soruyu sınıflandır. Sadece şu kelimelerden birini yaz: SQL, ANOMALY, BOTH

- SQL: veri sorgulama sorusu (en iyi, en çok, kaç tane, hangi sektör vs.)
- ANOMALY: anomali, sapma, neden düştü, neden yükseldi soruları
- BOTH: hem veri hem yorum gerektiriyor

SORU: {question}
SINIF:"""

    classification = llm.invoke(classify_prompt).content.strip().upper()
    
    results = []

    # 2. sınıfa göre tool çalıştır
    if "ANOMALY" in classification:
        # hangi metrik soruluyor?
        metric_prompt = f"""
Şu sorudan hangi metrik sorgulanıyor? 
Sadece şunlardan birini yaz: revenue, deals, win_rate, sales_rep, days_to_close, pipeline

SORU: {question}
METRİK:"""
        metric = llm.invoke(metric_prompt).content.strip().lower()
        if metric not in ["revenue", "deals", "win_rate"]:
            metric = "revenue"
        anomaly_result = anomaly_tool.invoke(metric)
        results.append(anomaly_result)

    else:
        sql_result = sql_query_tool.invoke(question)
        results.append(sql_result)

    # 3. sonucu yorumla
    combined = "\n\n".join(results)
    insight = insight_tool.invoke(combined)
    
    return insight