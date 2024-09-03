import requests
import time
import json
import os
from bs4 import BeautifulSoup

# Fetch the BASE_URL from the environment variable, with a default value if not set
BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")
LOG_DIR = "user_session_logs/mturk"

def generate_url(session_id):
    return f"{BASE_URL}/{session_id}"

def fetch_instruction(session_id):
    url = generate_url(session_id)
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        instruction_div = soup.find('div', id='instruction-text')
        if instruction_div:
            instruction_text = instruction_div.find('h4').get_text(strip=True)
            return instruction_text.replace('Instruction: ', '')
    return None

def monitor_log(session_id):
    log_file = os.path.join(LOG_DIR, f"{session_id}.jsonl")
    while True:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.readlines()
                if logs:
                    last_log = json.loads(logs[-1])
                    if last_log.get('page') == 'done':
                        print(f"User reached end state for session {session_id}")
                        print("stop")
                        break
        time.sleep(1)

def generate_session_ids(start, end):
    return [f"fixed_{i}" for i in range(start, end + 1)]

def establish_connection(max_retries=5, sleep_time=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(BASE_URL)
            if response.status_code == 200:
                print(f"Successfully connected to {BASE_URL}")
                return True
        except requests.ConnectionError:
            print(f"Connection attempt {attempt + 1} failed. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
    print(f"Failed to establish connection to {BASE_URL} after {max_retries} attempts.")
    return False

def main():
    if not establish_connection():
        print("Exiting due to connection failure.")
        return

    # Read session ID range from environment variables
    session_id_start = int(os.environ.get("SESSION_ID_START", 0))
    session_id_end = int(os.environ.get("SESSION_ID_END", 1000))

    session_ids = generate_session_ids(session_id_start, session_id_end)  # Use environment variables
    for session_id in session_ids:
        print(f"Running session: {session_id}")
        url = generate_url(session_id)
        print(f"Generated URL: {url}")
        instruction = fetch_instruction(session_id)
        if instruction:
            print(f"Instruction for {session_id}: {instruction}")
        else:
            print(f"Failed to fetch instruction for {session_id}")

        print("Waiting for user to navigate...")
        monitor_log(session_id)

        print("Moving to next session")

if __name__ == "__main__":
    main()