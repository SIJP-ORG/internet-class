import sqlite3
from flask import current_app, g

def init_app(app):
    app.teardown_appcontext(close_db)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = dict_factory

    return g.db

def close_db(e=None):
    '''Closing database connection. It's automatically called at app tear down.'''
    db = g.pop('db', None)
    if db is not None:
        db.close()

def dict_factory(cursor, row):
    '''return query as Python dict'''
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def init_db():
    '''Clear the existing data and create new tables.'''
    db = get_db()
    with current_app.open_resource('schema.sql') as sql:
        db.executescript(sql.read().decode('utf8'))
    return 'Initialized the database.'