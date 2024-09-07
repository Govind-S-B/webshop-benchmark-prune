from flask import Flask, jsonify, request, send_file
import threading
import time
import os
import shutil

import requests
import json
from bs4 import BeautifulSoup

import csv

app = Flask(__name__)

# Global variables for observer state
observer_running = False
observer_thread = None
session_details = []  # List to store session details to write in csv


log_directory = "user_session_logs/mturk"
BASE_URL = os.environ.get("INTERNAL_URL", "http://localhost:3000")
DISPLAY_URL = os.environ.get("EXTERNAL_ACCESS_URL", "http://localhost:3000")

def generate_display_url(session_id):
    return f"{DISPLAY_URL}/{session_id}"

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


API_KEY = os.environ.get('NFIG_API_KEY')

def create_workflow(goal):
    url = "https://api-dev.nfig.ai/external-apis/request/workflow/autonomous/create"
    headers = {
        'api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        "goal": goal
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("workflowId")
    return None

def run_workflow(workflow_id):
    url = "https://api-dev.nfig.ai/external-apis/request/workflow/autonomous/run"
    headers = {
        'api-key': API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        "workflowId": workflow_id
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("sessionId")
    return None

def stop_workflow(session_id):
    url = f"https://api-dev.nfig.ai/external-apis/request/workflow/autonomous/stop/{session_id}"
    headers = {
        'api-key': API_KEY,
        'Content-Type': 'application/json',
    }
    response = requests.post(url, headers=headers)
    return response.status_code == 200

def write_csv():
    """
    Function to write session details to a CSV file.
    """
    global session_details
    csv_file = os.path.join(log_directory, "session_details.csv")
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=["session_id", "url", "nfig_session_id"])
        writer.writeheader()
        writer.writerows(session_details)
    print(f"Session details written to {csv_file}")

def monitor_log(nfig_session_id, session_id):
    log_file = os.path.join(log_directory, f"{session_id}.jsonl")
    start_time = time.time()
    timeout = 5 * 60  # 5 minutes in seconds

    while observer_running:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = f.readlines()
                if logs:
                    last_log = json.loads(logs[-1])
                    if last_log.get('page') == 'done':
                        print(f"User reached end state for session {session_id}")
                        print("stop") # [API REQ] this will in production call an API to my server to terminate a task

                        stop_workflow(nfig_session_id)
                        break

        # Check for timeout
        if time.time() - start_time > timeout:
            print(f"Timeout reached for session {session_id}")
            stop_workflow(nfig_session_id)
            break

        time.sleep(1)

def observer_task(session_ids):
    """
    Function to monitor logs and process session IDs.
    """
    global observer_running
    observer_running = True
    
    for session_id in session_ids:
        if not observer_running:
            break
        print(f"Running session: {session_id}")
        url = generate_display_url(session_id)
        print(f"Generated URL: {url}") # [API REQ] this will in production make an API call to my server to init a task

        workflow_id = create_workflow(f"Go to {url} and follow the instruction mentioned there to complete the order on the platform")

        instruction = fetch_instruction(session_id)
        if instruction:
            print(f"Instruction for {session_id}: {instruction}") # [API REQ] this will also go with the above mentioned API call

            # uncomment this section if you want to pass the actual instruction as well to goal
            # workflow_id = create_workflow(f"Go to {url} and order the following product : {instruction}")

        else:
            print(f"Failed to fetch instruction for {session_id}")

        nfig_session_id = run_workflow(workflow_id)

        # Append session details to the list
        session_details.append({
            "session_id": session_id,
            "url": url,
            "nfig_session_id": nfig_session_id
        })

        print("Waiting for user to navigate...")
        monitor_log(nfig_session_id,session_id)

        print("Moving to next session")
    observer_running = False
    print("Observer task completed.")
    write_csv()
    
def clear_session_details():
    """
    Function to clear the session details list.
    """
    global session_details
    session_details = []

@app.route('/start', methods=['POST'])
def start_observer():
    """
    API endpoint to start the observer task.
    It checks if the observer is already running and starts a thread if not.
    """
    global observer_thread, observer_running
    if observer_running:
        return jsonify({"status": "already running"}), 400

    clear_session_details()  # Clear session details before starting a new task

    session_ids = request.json.get("session_ids")
    if not session_ids:
        start = int(request.json.get("start", 0))
        end = int(request.json.get("end", 1000))
        session_ids = [f"fixed_{i}" for i in range(start, end + 1)]

    observer_thread = threading.Thread(target=observer_task, args=(session_ids,))
    observer_thread.start()
    return jsonify({"status": "started"}), 200

@app.route('/stop', methods=['POST'])
def stop_observer():
    """
    API endpoint to stop the observer task.
    It sets a flag to terminate the task gracefully.
    """
    global observer_running
    observer_running = False
    if observer_thread:
        observer_thread.join()  # Wait for the thread to finish if it's running
    return jsonify({"status": "stopped"}), 200

@app.route('/clean', methods=['POST'])
def clean_logs():
    """
    API endpoint to clean the log directory.
    It deletes all files in the specified directory and clears session details.
    """
    clear_session_details()  # Clear session details when cleaning logs

    for filename in os.listdir(log_directory):
        file_path = os.path.join(log_directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return jsonify({"status": "cleaned"}), 200

@app.route('/status', methods=['GET'])
def get_status():
    """
    API endpoint to get the current status of the observer.
    It returns whether the observer is running and the current session details.
    """
    current_status = {
        "running": observer_running,
        "current_session": session_details[-1] if session_details else None
    }
    return jsonify(current_status), 200

@app.route('/save', methods=['POST'])
def save_session():
    """
    API endpoint to save the current logs with a given name.
    It moves the contents of the log directory to a new location.
    """
    name = request.json.get("name", "default_name")
    target_directory = os.path.join(log_directory, "../", name)
    os.makedirs(target_directory, exist_ok=True)
    
    for filename in os.listdir(log_directory):
        file_path = os.path.join(log_directory, filename)
        if os.path.isfile(file_path):
            shutil.move(file_path, os.path.join(target_directory, filename))
    
    return jsonify({"status": f"session saved as {name}"}), 200

@app.route('/get', methods=['GET'])
def get_session():
    """
    API endpoint to compress and provide the saved session logs.
    It returns the logs as a zip file.
    """
    name = request.args.get("name", "default_name")
    target_directory = os.path.join(log_directory, "../", name)
    archive_name = shutil.make_archive(target_directory, 'zip', target_directory)
    
    return send_file(archive_name, as_attachment=True, download_name=f"{name}.zip")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)