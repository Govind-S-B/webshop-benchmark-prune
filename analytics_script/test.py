import csv
import json
import os
import requests
from collections import defaultdict
from statistics import mean

# Function to read CSV file
def read_csv(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        return list(reader)

# Function to read JSONL file
def read_jsonl(file_path):
    with open(file_path, mode='r') as file:
        return [json.loads(line) for line in file]

# Function to get Portkey information
def get_portkey_info(trace_id, api_key):
    url = f"https://api.portkey.ai/v1/traces/{trace_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Function to process session details and observer logs
def process_sessions(session_details, observer_logs_dir, portkey_api_key):
    completed_sessions = []
    timeout_sessions = []
    all_sessions = []

    page_visits = defaultdict(lambda: {'all': 0, 'completed': 0, 'timeout': 0})

    for session in session_details:
        session_id = session['session_id']
        log_file_path = os.path.join(observer_logs_dir, f"{session_id}.jsonl")

        if os.path.exists(log_file_path):
            log_contents = read_jsonl(log_file_path)
            print(f"CSV Record: {session}")
            print(f"Log Contents: {log_contents}")

            # Dump Portkey information
            for log in log_contents:
                trace_id = log.get('trace_id')
                if trace_id:
                    portkey_info = get_portkey_info(trace_id, portkey_api_key)
                    print(f"Portkey Info for Trace ID {trace_id}: {portkey_info}")

            # Update page visits
            for log in log_contents:
                page = log['page']
                page_visits[page]['all'] += 1
                if session['session_termination_reason'] == 'completed':
                    page_visits[page]['completed'] += 1
                elif session['session_termination_reason'] == 'timeout':
                    page_visits[page]['timeout'] += 1

            # Categorize sessions
            all_sessions.append(session)
            if session['session_termination_reason'] == 'completed':
                completed_sessions.append(session)
            elif session['session_termination_reason'] == 'timeout':
                timeout_sessions.append(session)

    return all_sessions, completed_sessions, timeout_sessions, page_visits

# Function to print summary statistics
def print_summary(all_sessions, completed_sessions, timeout_sessions, page_visits):
    print(f"Total Sessions: {len(all_sessions)}")
    print(f"Completed Sessions: {len(completed_sessions)}")
    print(f"Timeout Sessions: {len(timeout_sessions)}")

    if timeout_sessions:
        avg_timeout_steps = mean(int(session['navigation_steps']) for session in timeout_sessions)
        print(f"Average Steps in Timeout Sessions: {avg_timeout_steps}")

    if completed_sessions:
        avg_completed_time = mean(float(session['duration']) for session in completed_sessions)
        avg_completed_steps = mean(int(session['navigation_steps']) for session in completed_sessions)
        avg_completed_score = mean(float(session['session_score']) for session in completed_sessions)
        print(f"Average Time in Completed Sessions: {avg_completed_time}")
        print(f"Average Steps in Completed Sessions: {avg_completed_steps}")
        print(f"Average Score in Completed Sessions: {avg_completed_score}")

        success_sessions = [session for session in completed_sessions if float(session['session_score']) == 1.0]
        success_ratio_all = len(success_sessions) / len(all_sessions)
        success_ratio_completed = len(success_sessions) / len(completed_sessions)
        print(f"Success Ratio (All Sessions): {success_ratio_all}")
        print(f"Success Ratio (Completed Sessions): {success_ratio_completed}")

    print("Page Visits:")
    for page, counts in page_visits.items():
        print(f"{page}: All: {counts['all']}, Completed: {counts['completed']}, Timeout: {counts['timeout']}")

# Main function
def main():
    session_details_file = 'analytics_script/observer_logs/session_details.csv'
    observer_logs_dir = 'analytics_script/observer_logs'
    portkey_api_key = 'YOUR_PORTKEY_API_KEY'  # Replace with your actual Portkey API key

    session_details = read_csv(session_details_file)
    all_sessions, completed_sessions, timeout_sessions, page_visits = process_sessions(session_details, observer_logs_dir, portkey_api_key)
    print_summary(all_sessions, completed_sessions, timeout_sessions, page_visits)

if __name__ == "__main__":
    main()