from dotenv import load_dotenv
from pathlib import Path
import os



BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def _required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DB_URL = _required_env('DB_URL')
SECRET_KEY = _required_env('SECRET_KEY')


