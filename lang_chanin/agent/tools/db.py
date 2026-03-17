import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / ".env")

engine = create_engine(
    f"postgresql://postgres:{os.getenv('DB_PASSWORD')}@db.tzqnzapkgjwsszqgjrie.supabase.co:5432/postgres?sslmode=require",
    connect_args={"host": "db.tzqnzapkgjwsszqgjrie.supabase.co"}
)