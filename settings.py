import os

from dotenv import load_dotenv
from orator import DatabaseManager

load_dotenv(verbose=True)

databases = {
    'postgres': {
        'driver': 'postgres',
        'host': 'localhost',
        'database': 'postgres',
        'user': 'postgres',
        'password': '',
        'prefix': ''
    }
}

db = DatabaseManager(databases)

BOT_TOKEN = os.getenv("BOT_TOKEN")
