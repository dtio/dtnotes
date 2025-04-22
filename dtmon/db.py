# db.py
import psycopg2
import psycopg2.extras
from flask import g, current_app

def get_db():
    """
    Establishes and returns a database connection.  Uses the application context
    to store the connection.
    """
    if 'db' not in g:
        try:
            g.db = psycopg2.connect(current_app.config['DATABASE_URL'])
        except psycopg2.Error as e:
            print(f"Database connection error: {e}")
            return None
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    db = get_db()
    if db is None:  # Handle the case where the database connection failed
        return None
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)  # Use DictCursor
    try:
        cursor.execute(query, args)
        rv = cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Database query error: {e}")
        rv = None
    finally:
        cursor.close()
    return (rv[0] if rv and one else None) if one else rv
    

def execute_db(query, args=()):
    """
    Executes a database command (e.g., INSERT, UPDATE, DELETE).
    """
    db = get_db()
    if db is None:
        return False  # Handle the case where get_db() failed
    cur = db.cursor()
    try:
        cur.execute(query, args)
        db.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        db.rollback()
        cur.close()
        return False

def init_db():
    """
    Initializes the database by executing the schema.sql script.
    """
    db = get_db()
    if db is None:
        return
    with current_app.open_resource('schema.sql', mode='r') as f:
        cursor = db.cursor()
        cursor.execute(f.read())
        db.commit()
        cursor.close()
        print("Database initialized.")

def get_user(username):
    """
    Retrieves a user from the database based on their username.
    """
    return query_db('SELECT user_id, username, password_hash, role FROM users WHERE username = %s', (username,), one=True)
