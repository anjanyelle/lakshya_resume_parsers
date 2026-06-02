from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("No DATABASE_URL found in .env")
    exit(1)

print(f"Connecting to: {database_url}")
try:
    engine = create_engine(database_url)
    with engine.connect() as conn:
        print("Successfully connected to the database.")
except Exception as e:
    print(f"Failed to connect: {e}")
