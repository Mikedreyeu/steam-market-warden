import os

from dotenv import load_dotenv


load_dotenv(verbose=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_FOR_ERRORS = os.getenv("CHAT_FOR_ERRORS")
