import os

from dotenv import load_dotenv
from orator import DatabaseManager

databases = {
    'postgres': {
        'driver': 'postgres',
        'host': 'localhost',
        'database': 'steamwarden',
        'user': 'postgres',
        'password': '1111',
        'prefix': ''
    }
}

db = DatabaseManager(databases)

load_dotenv(verbose=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_FOR_ERRORS = os.getenv("CHAT_FOR_ERRORS")
