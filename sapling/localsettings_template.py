import os

DEBUG = True
CACHE_BACKEND = 'dummy:///'

DATABASE_ENGINE = 'sqlite3'
# Or path to database file if using sqlite3.
DATABASE_NAME = os.path.join(os.path.dirname(__file__), 'dev.db')
# Not used with sqlite3.
DATABASE_USER = ''
# Not used with sqlite3.
DATABASE_PASSWORD = ''
# Set to empty string for localhost. Not used with sqlite3.
DATABASE_HOST = ''
DATABASE_PORT = ''
