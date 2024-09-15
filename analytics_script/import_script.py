import csv
import json
import os
import sqlite3
from collections import defaultdict

def read_csv(file_path):
    """Read a CSV file and return a list of dictionaries."""
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)

def read_jsonl(file_path):
    """Read a JSONL file and return a list of JSON objects."""
    with open(file_path, mode='r', encoding='utf-8') as file:
        return [json.loads(line) for line in file]

def initialize_database(db_path):
    """Initialize the SQLite database with a flat sessions table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create sessions table with additional count_page_<pagename> columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            trace_id TEXT,
            session_termination_reason TEXT,
            duration REAL,
            portkey_match_count INTEGER,
            session_tokens INTEGER,
            session_cost REAL,
            session_score REAL,
            r_type REAL,
            r_att REAL,
            w_att REAL,
            query_match BOOLEAN,
            category_match BOOLEAN,
            title_score REAL,
            r_option REAL,
            w_option REAL,
            r_price BOOLEAN,
            w_price REAL,
            navigation_steps INTEGER,
            count_page_index INTEGER DEFAULT 0,
            count_page_search_results INTEGER DEFAULT 0,
            count_page_item_page INTEGER DEFAULT 0,
            count_page_item_sub_page INTEGER DEFAULT 0,
            count_page_done INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    return conn

def safe_float(value, default=0.0):
    """Convert a value to float safely, returning a default value if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """Convert a value to int safely, returning a default value if conversion fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_bool(value, default=False):
    """Convert a value to bool safely, returning a default value if conversion fails."""
    try:
        return bool(value)
    except (ValueError, TypeError):
        return default

def insert_session(conn, session):
    """Insert a session into the sessions table."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO sessions (
            session_id, trace_id, session_termination_reason, duration, 
            portkey_match_count, session_tokens, session_cost, session_score,
            r_type, r_att, w_att, query_match, category_match, 
            title_score, r_option, w_option, r_price, w_price,
            navigation_steps,
            count_page_index, count_page_search_results, 
            count_page_item_page, count_page_item_sub_page, count_page_done
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        session.get('session_id'),
        session.get('trace_id'),
        session.get('session_termination_reason'),
        safe_float(session.get('duration', 0)),
        safe_int(session.get('portkey_match_count', 0)),
        safe_int(session.get('session_tokens', 0)),
        safe_float(session.get('session_cost', 0.0)),
        safe_float(session.get('session_score', 0)),
        safe_float(session.get('r_type', 0.0)),
        safe_float(session.get('r_att', 0.0)),
        safe_float(session.get('w_att', 0.0)),
        safe_bool(session.get('query_match', False)),
        safe_bool(session.get('category_match', False)),
        safe_float(session.get('title_score', 0.0)),
        safe_float(session.get('r_option', 0.0)),
        safe_float(session.get('w_option', 0.0)),
        safe_bool(session.get('r_price', False)),
        safe_float(session.get('w_price', 0.0)),
        safe_int(session.get('navigation_steps', 0)),
        safe_int(session.get('count_page_index', 0)),
        safe_int(session.get('count_page_search_results', 0)),
        safe_int(session.get('count_page_item_page', 0)),
        safe_int(session.get('count_page_item_sub_page', 0)),
        safe_int(session.get('count_page_done', 0))
    ))
    conn.commit()

def process_sessions(session_details, observer_logs_dir, portkey_data, conn):
    """Process sessions and insert data into the database."""
    # Define the pages to count
    pages_to_count = [
        'search_results',
        'index',
        'done',
        'item_page',
        'item_sub_page'
    ]

    for session in session_details:
        session_id = session['session_id']
        trace_id = session['nfig_session_id']
        log_file_path = os.path.join(observer_logs_dir, f"{session_id}.jsonl")
        
        # Initialize default values
        session['portkey_match_count'] = 0
        session['session_tokens'] = 0
        session['session_cost'] = 0.0
        # Initialize reward_info fields
        session['r_type'] = 0.0
        session['r_att'] = 0.0
        session['w_att'] = 0.0
        session['query_match'] = False
        session['category_match'] = False
        session['title_score'] = 0.0
        session['r_option'] = 0.0
        session['w_option'] = 0.0
        session['r_price'] = False
        session['w_price'] = 0.0

        # Initialize page counts
        for page in pages_to_count:
            session[f'count_page_{page}'] = 0
        
        if os.path.exists(log_file_path):
            log_contents = read_jsonl(log_file_path)
            
            # Find matching Portkey data
            portkey_info = [entry for entry in portkey_data if entry['TRACE ID'] == trace_id]
            session['portkey_match_count'] = len(portkey_info)
            
            # Update tokens and cost
            for entry in portkey_info:
                session['session_tokens'] += int(entry.get('TOKENS', 0))
                # Assuming 'COST' is a string like "0.05 USD"
                cost_str = entry.get('COST', '0').split()[0]
                try:
                    session['session_cost'] += float(cost_str)
                except ValueError:
                    session['session_cost'] += 0.0
            
            # Extract reward_info fields and count pages from logs
            for log in log_contents:
                # Count pages
                page = log.get('page')
                if page in pages_to_count:
                    session[f'count_page_{page}'] += 1

                # Update reward_info
                reward_info = log.get('reward_info', {})
                if reward_info:
                    # Update only if the key exists in reward_info
                    if 'r_type' in reward_info:
                        session['r_type'] = float(reward_info.get('r_type', 0.0))
                    if 'r_att' in reward_info:
                        session['r_att'] = float(reward_info.get('r_att', 0.0))
                    if 'w_att' in reward_info:
                        session['w_att'] = float(reward_info.get('w_att', 0.0))
                    if 'query_match' in reward_info:
                        session['query_match'] = bool(reward_info.get('query_match', False))
                    if 'category_match' in reward_info:
                        session['category_match'] = bool(reward_info.get('category_match', False))
                    if 'title_score' in reward_info:
                        session['title_score'] = float(reward_info.get('title_score', 0.0))
                    if 'r_option' in reward_info:
                        session['r_option'] = float(reward_info.get('r_option', 0.0))
                    if 'w_option' in reward_info:
                        session['w_option'] = float(reward_info.get('w_option', 0.0))
                    if 'r_price' in reward_info:
                        session['r_price'] = bool(reward_info.get('r_price', False))
                    if 'w_price' in reward_info:
                        session['w_price'] = float(reward_info.get('w_price', 0.0))
                    # Assuming only one reward_info per session or taking the last one
        
        # Insert session into sessions table
        insert_session(conn, session)

def main():
    # File paths
    session_details_file = 'analytics_script/observer_logs/session_details.csv'
    observer_logs_dir = 'analytics_script/observer_logs'
    portkey_csv_file = 'analytics_script/observer_logs/portkey.csv'
    db_path = 'analytics_script/analytics.db'
    
    # Read data
    session_details = read_csv(session_details_file)
    
    # Read Portkey data
    if os.path.exists(portkey_csv_file):
        portkey_data = read_csv(portkey_csv_file)
    else:
        portkey_data = []
    
    # Initialize database
    conn = initialize_database(db_path)
    
    # Process and insert data
    process_sessions(session_details, observer_logs_dir, portkey_data, conn)
    
    # Close connection
    conn.close()
    print("Data import completed successfully.")

if __name__ == "__main__":
    main()