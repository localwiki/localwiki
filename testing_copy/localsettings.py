#CACHE_BACKEND = 'dummy:///'
import os

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'saplingwiki'             # Or path to database file if using sqlite3.
DATABASE_USER = 'sapling'             # Not used with sqlite3.
DATABASE_PASSWORD = 'lFLF5886879FCSDFer3ccc#$!56'         # Not used with sqlite3.
DATABASE_HOST = '127.0.0.1'             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
#DATABASE_ENGINE = 'sqlite3'
#DATABASE_NAME = 'dev.db'

DEBUG = True

DAISYDIFF_URL = 'http://localhost:8080/diff'
DAISYDIFF_MERGE_URL = 'http://localhost:8080/merge'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/philip/projects/sapling/sapling_project/templates',
)
