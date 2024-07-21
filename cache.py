import json
import sqlite3
import requests
from datetime import datetime, timedelta

def create_table():
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER NOT NULL,
        response TEXT NOT NULL,
        stored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def cache_api_response(player_id, json_response):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO cache (player_id, response, stored_at)
        VALUES(?, ?, ?)               
    ''', (player_id, json.dumps(json_response), datetime.now()))

    conn.commit()
    conn.close()

def get_cached_response(player_id, max_age_minutes = 10):
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT response, stored_at FROM cache
        WHERE player_id = ?
    ''', (player_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        response, stored_at = row
        stored_at = datetime.fromisoformat(stored_at)

        if datetime.now() - stored_at < timedelta(minutes = max_age_minutes):
            json.loads(response)

        return None
    
def delete_old_cached_responses(max_age_minutes = 10):
    threshold_time = datetime.now() - timedelta(minutes=max_age_minutes)
    conn = sqlite3.connect('cache.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM cache
        WHERE stored_at < ?
    ''', (threshold_time.isoformat(),))
    
    conn.commit()
    conn.close()

def fetch_api_data(endpoint, player_id):
    # Check for a cached response
    cached = get_cached_response(player_id)

    if cached:
        return cached
    
    response = requests.get(endpoint)

    if response.status_code == 200:
        json_response = response.json()
        cache_api_response(player_id, json_response)
        delete_old_cached_responses()
        return json_response
    else:
        return None
    
create_table()