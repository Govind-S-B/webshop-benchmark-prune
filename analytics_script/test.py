import csv
import json
import os
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

# Function to process session details and observer logs
def process_sessions(session_details, observer_logs_dir, portkey_data):
    completed_sessions = []
    timeout_sessions = []
    all_sessions = []

    page_visits = defaultdict(lambda: {'all': 0, 'completed': 0, 'timeout': 0})
    total_tokens = 0
    total_cost = 0.0

    for session in session_details:
        session_id = session['session_id']
        trace_id = session['nfig_session_id']
        log_file_path = os.path.join(observer_logs_dir, f"{session_id}.jsonl")

        if os.path.exists(log_file_path):
            log_contents = read_jsonl(log_file_path)
            print("-" * 50)
            print(f"CSV Record:\n{json.dumps(session, indent=4)}\n")
            print(f"Log Contents:\n{json.dumps(log_contents, indent=4)}\n")

            # Find matching Portkey data
            portkey_info = [entry for entry in portkey_data if entry['TRACE ID'] == trace_id]
            print(f"Portkey Info for Trace ID {trace_id}:\n{json.dumps(portkey_info, indent=4)}\n")

            # Update tokens and cost
            for entry in portkey_info:
                total_tokens += int(entry['TOKENS'])
                total_cost += float(entry['COST'].split()[0])

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

    return all_sessions, completed_sessions, timeout_sessions, page_visits, total_tokens, total_cost

# Function to print summary statistics
def print_summary(all_sessions, completed_sessions, timeout_sessions, page_visits, total_tokens, total_cost):
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

    print(f"Total Tokens Used: {total_tokens}")
    print(f"Total Cost: {total_cost} cents")

    print("Page Visits:")
    for page, counts in page_visits.items():
        print(f"{page}: All: {counts['all']}, Completed: {counts['completed']}, Timeout: {counts['timeout']}")

# Main function
def main():
    session_details_file = 'analytics_script/observer_logs/session_details.csv'
    observer_logs_dir = 'analytics_script/observer_logs'
    portkey_csv_file = 'analytics_script/observer_logs/portkey.csv'

    session_details = read_csv(session_details_file)
    portkey_data = read_csv(portkey_csv_file)
    all_sessions, completed_sessions, timeout_sessions, page_visits, total_tokens, total_cost = process_sessions(session_details, observer_logs_dir, portkey_data)
    print_summary(all_sessions, completed_sessions, timeout_sessions, page_visits, total_tokens, total_cost)

if __name__ == "__main__":
    main()