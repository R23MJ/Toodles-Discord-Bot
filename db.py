import sqlite3

# Connect to the SQLite database (it will create the database file if it does not exist)
def get_connection():
    conn = sqlite3.connect('api_keys.db')
    return conn

# Create the table if it doesn't exist
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS api_keys (
        server_id TEXT PRIMARY KEY,
        api_key TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Insert or update an API key
def set_api_key(server_id, api_key):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO api_keys (server_id, api_key)
    VALUES (?, ?)
    ON CONFLICT(server_id) DO UPDATE SET api_key = excluded.api_key
    ''', (server_id, api_key))
    conn.commit()
    conn.close()

# Retrieve an API key
def get_api_key(server_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT api_key FROM api_keys WHERE server_id = ?', (server_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Initialize the database
create_table()