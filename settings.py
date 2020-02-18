import os
import re

from dotenv import load_dotenv
from orator import DatabaseManager


load_dotenv(verbose=True)

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_FOR_ERRORS = int(os.getenv('CHAT_FOR_ERRORS'))
CHAT_FOR_REQUESTS = int(os.getenv('CHAT_FOR_REQUESTS'))
ADMIN_ID = int(os.getenv('ADMIN_ID'))
DATABASE_URL = os.getenv('DATABASE_URL')

DATABASE_URL_REGEX = r'postgres://(?P<user>.+):(?P<password>.+)@(?P<host>.+):(?P<port>\d+)/(?P<database>.+)'

database_url_match = re.fullmatch(DATABASE_URL_REGEX, DATABASE_URL)

databases = {
    'postgres': {
        'driver': 'postgres',
        'host': database_url_match.group('host'),
        'database': database_url_match.group('database'),
        'user': database_url_match.group('user'),
        'password': database_url_match.group('password'),
        'prefix': ''
    }
}

db = DatabaseManager(databases)
