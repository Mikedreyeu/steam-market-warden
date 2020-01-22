from orator import DatabaseManager

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
