import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")
print(f".env path: {env_path}")
print(f".env exists: {env_path.exists()}")
