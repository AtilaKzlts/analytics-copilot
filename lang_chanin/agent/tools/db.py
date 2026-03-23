import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / ".env")

engine = create_engine(
    os.getenv("NEON_CONNECTION"),
    pool_pre_ping=True,       # bağlantı kopuksa otomatik yenile
    pool_recycle=300,         # her 5 dakikada bağlantıyı yenile
    pool_size=5,
    max_overflow=2
)