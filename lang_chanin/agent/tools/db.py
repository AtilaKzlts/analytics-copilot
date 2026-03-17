import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / ".env")

engine = create_engine(os.getenv("NEON_CONNECTION"))