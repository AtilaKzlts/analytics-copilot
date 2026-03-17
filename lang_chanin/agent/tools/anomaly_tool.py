import os
import pandas as pd
from sqlalchemy import text
from langchain.tools import tool
from pathlib import Path
from dotenv import load_dotenv
from agent.tools.db import engine

load_dotenv(Path(__file__).parent.parent.parent / ".env")


AVAILABLE_METRICS = {
    "revenue":       "Aylık toplam gelir",
    "deals":         "Aşama bazında deal sayısı",
    "win_rate":      "Sektör bazında win rate",
    "sales_rep":     "Satışçı bazında kazanılan gelir",
    "days_to_close": "Satışçı bazında ortalama kapanma süresi",
    "pipeline":      "Sektör bazında pipeline değeri",
}

queries = {
    "revenue": """
        SELECT revenue_month::text, total_revenue
        FROM raw.monthly_revenue
        WHERE revenue_type = 'Recurring'
        ORDER BY revenue_month
    """,
    "deals": """
        SELECT stage, deal_count
        FROM raw.deal_funnel
        ORDER BY deal_count DESC
    """,
    "win_rate": """
        SELECT industry, win_rate_pct
        FROM raw.pipeline_by_industry
        ORDER BY win_rate_pct DESC
    """,
    "sales_rep": """
        SELECT sales_rep, total_won_revenue
        FROM raw.sales_rep_performance
        ORDER BY total_won_revenue DESC
    """,
    "days_to_close": """
        SELECT sales_rep, avg_days_to_close
        FROM raw.sales_rep_performance
        WHERE avg_days_to_close IS NOT NULL
        ORDER BY avg_days_to_close DESC
    """,
    "pipeline": """
        SELECT industry, total_pipeline_value
        FROM raw.pipeline_by_industry
        ORDER BY total_pipeline_value DESC
    """,
}

@tool
def anomaly_tool(metric: str) -> str:
    """
    Verilen metrikte istatistiksel anomali tespit eder.
    Kullanılabilir metrikler: revenue, deals, win_rate,
    sales_rep, days_to_close, pipeline
    """

    # bilinmeyen metrik gelirse en yakını bul
    if metric not in queries:
        metric = "revenue"

    with engine.connect() as conn:
        df = pd.read_sql(text(queries[metric]), conn)

    if df.empty:
        return "Veri bulunamadı."

    col = df.columns[1]
    mean = df[col].mean()
    std  = df[col].std()

    if std == 0:
        return f"{metric} metriğinde tüm değerler aynı, anomali yok."

    df["z_score"] = (df[col] - mean) / std
    anomalies = df[df["z_score"].abs() > 2]

    # özet istatistik her zaman göster
    result  = f"Metrik: {AVAILABLE_METRICS.get(metric, metric)}\n"
    result += f"Ortalama: {mean:,.2f} | Std Sapma: {std:,.2f}\n"
    result += f"Min: {df[col].min():,.2f} | Max: {df[col].max():,.2f}\n"
    result += "-" * 50 + "\n"

    if anomalies.empty:
        result += "Anomali tespit edilmedi. Değerler normal aralıkta.\n\n"
    else:
        result += f"{len(anomalies)} anomali bulundu:\n\n"
        for _, row in anomalies.iterrows():
            direction = "⬆ YÜKSEK" if row["z_score"] > 0 else "⬇ DÜŞÜK"
            result += f"{row.iloc[0]} → {row[col]:,.2f} ({direction}, z={row['z_score']:.2f})\n"

    # tüm veriyi de ekle, insight_tool daha iyi yorum yapsın
    result += "\nTüm veri:\n"
    for _, row in df.iterrows():
        result += f"  {row.iloc[0]}: {row[col]:,.2f}\n"

    return result