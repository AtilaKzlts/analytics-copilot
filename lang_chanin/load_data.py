import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(Path(__file__).parent / ".env")

engine = create_engine(os.getenv("NEON_CONNECTION"))

# raw schema oluştur
with engine.begin() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))

files = {
    "deals":      "data/raw/deals.csv",
    "companies":  "data/raw/companies.csv",
    "contacts":   "data/raw/contacts.csv",
    "activities": "data/raw/activities.csv",
    "revenues":   "data/raw/revenues.csv",
}

for table_name, path in files.items():
    df = pd.read_csv(path)
    df.to_sql(table_name, engine, schema="raw", if_exists="replace", index=False)
    print(f"{table_name}: {len(df)} satır yüklendi")

print("\nTüm tablolar Supabase'e yüklendi!")