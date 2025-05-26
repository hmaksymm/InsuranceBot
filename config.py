import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MINDEE_API_KEY = os.getenv("MINDEE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INSURANCE_PRICE_USD = int(os.getenv("INSURANCE_PRICE_USD", 100))
MINDEE_ENDPOINT = os.getenv("MINDEE_ENDPOINT")
