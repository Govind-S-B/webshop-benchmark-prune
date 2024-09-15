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
def process_sessions(session_details, observer_logs_dir, portkey_data, output_file):
    completed_sessions = []
    timeout_sessions = []
    all_sessions = []

    page_visits = defaultdict(lambda: {'all': 0, 'completed': 0, 'timeout': 0})
    total_tokens = 0
    total_cost = 0.0
    total_time = 0.0  # Initialize total time

    # Additional metrics aggregation
    reward_info_aggregates = defaultdict(lambda: {'total': 0.0, 'count': 0})

    for session in session_details:
        session_id = session['session_id']
        trace_id = session['nfig_session_id']
        log_file_path = os.path.join(observer_logs_dir, f"{session_id}.jsonl")

        if os.path.exists(log_file_path):
            log_contents = read_jsonl(log_file_path)
            output_file.write("-" * 50 + "\n")
            output_file.write(f"CSV Record:\n{json.dumps(session, indent=4)}\n\n")
            output_file.write(f"Log Contents:\n{json.dumps(log_contents, indent=4)}\n\n")

            # Find matching Portkey data
            portkey_info = [entry for entry in portkey_data if entry['TRACE ID'] == trace_id]
            output_file.write(f"Portkey Info for Trace ID {trace_id}:\n{json.dumps(portkey_info, indent=4)}\n\n")

            # Update tokens and cost
            session_tokens = 0
            session_cost = 0.0
            for entry in portkey_info:
                session_tokens += int(entry['TOKENS'])
                session_cost += float(entry['COST'].split()[0])
            total_tokens += session_tokens
            total_cost += session_cost

            # Update page visits and aggregate reward_info
            session_page_visits = defaultdict(int)
            for log in log_contents:
                page = log.get('page', 'unknown')
                page_visits[page]['all'] += 1
                session_page_visits[page] += 1
                termination_reason = session.get('session_termination_reason', 'unknown')
                if termination_reason == 'completed':
                    page_visits[page]['completed'] += 1
                elif termination_reason == 'timeout':
                    page_visits[page]['timeout'] += 1

                # Aggregate reward_info metrics
                reward_info = log.get('reward_info', {})
                for key, value in reward_info.items():
                    if isinstance(value, (int, float)):
                        reward_info_aggregates[key]['total'] += value
                        reward_info_aggregates[key]['count'] += 1

            # Categorize sessions
            session['portkey_match_count'] = len(portkey_info)
            session['session_tokens'] = session_tokens
            session['session_cost'] = session_cost
            session['session_page_visits'] = dict(session_page_visits)
            all_sessions.append(session)
            if session.get('session_termination_reason') == 'completed':
                completed_sessions.append(session)
            elif session.get('session_termination_reason') == 'timeout':
                timeout_sessions.append(session)

            # Add session duration to total time
            total_time += float(session.get('duration', 0))

            # Detailed session information in log dump
            output_file.write(f"Session ID: {session['session_id']}\n")
            output_file.write(f"Portkey Match Count: {session['portkey_match_count']}\n")
            output_file.write(f"Session Tokens: {session['session_tokens']}\n")
            output_file.write(f"Session Cost: {session['session_cost']} cents\n")
            output_file.write(f"Page Visits: {json.dumps(session['session_page_visits'], indent=4)}\n")
            output_file.write("-" * 50 + "\n")

    return all_sessions, completed_sessions, timeout_sessions, page_visits, total_tokens, total_cost, total_time, reward_info_aggregates

# Function to print summary statistics
def print_summary(all_sessions, completed_sessions, timeout_sessions, page_visits, total_tokens, total_cost, total_time, reward_info_aggregates, output_file):
    output_file.write("=" * 50 + "\n")
    output_file.write("Summary Statistics\n")
    output_file.write("=" * 50 + "\n")
    output_file.write(f"Total Sessions: {len(all_sessions)}\n")
    output_file.write(f"Completed Sessions: {len(completed_sessions)}\n")
    output_file.write(f"Timeout Sessions: {len(timeout_sessions)}\n\n")

    if timeout_sessions:
        avg_timeout_steps = mean(int(session.get('navigation_steps', 0)) for session in timeout_sessions)
        avg_timeout_cost = mean(session.get('session_cost', 0.0) for session in timeout_sessions)
        avg_timeout_tokens = mean(session.get('session_tokens', 0) for session in timeout_sessions)
        output_file.write(f"Average Steps in Timeout Sessions: {avg_timeout_steps}\n")
        output_file.write(f"Average Cost in Timeout Sessions: {avg_timeout_cost} cents\n")
        output_file.write(f"Average Tokens in Timeout Sessions: {avg_timeout_tokens}\n\n")

    if completed_sessions:
        avg_completed_time = mean(float(session.get('duration', 0)) for session in completed_sessions)
        avg_completed_steps = mean(int(session.get('navigation_steps', 0)) for session in completed_sessions)
        avg_completed_score = mean(float(session.get('session_score', 0)) for session in completed_sessions if session.get('session_score'))
        avg_completed_cost = mean(session.get('session_cost', 0.0) for session in completed_sessions)
        avg_completed_tokens = mean(session.get('session_tokens', 0) for session in completed_sessions)
        output_file.write(f"Average Time in Completed Sessions: {avg_completed_time}\n")
        output_file.write(f"Average Steps in Completed Sessions: {avg_completed_steps}\n")
        output_file.write(f"Average Score in Completed Sessions: {avg_completed_score}\n")
        output_file.write(f"Average Cost in Completed Sessions: {avg_completed_cost} cents\n")
        output_file.write(f"Average Tokens in Completed Sessions: {avg_completed_tokens}\n\n")

        success_sessions = [session for session in completed_sessions if float(session.get('session_score', 0)) == 1.0]
        success_ratio_all = len(success_sessions) / len(all_sessions) if all_sessions else 0
        success_ratio_completed = len(success_sessions) / len(completed_sessions) if completed_sessions else 0
        output_file.write(f"Success Ratio (All Sessions): {success_ratio_all}\n")
        output_file.write(f"Success Ratio (Completed Sessions): {success_ratio_completed}\n\n")

    output_file.write(f"Total Tokens Used: {total_tokens}\n")
    output_file.write(f"Total Cost: {total_cost} cents\n")
    output_file.write(f"Total Time: {total_time} seconds\n\n")  # Display total time

    output_file.write("Page Visits:\n")
    for page, counts in page_visits.items():
        output_file.write(f"{page}: All: {counts['all']}, Completed: {counts['completed']}, Timeout: {counts['timeout']}\n")

    # Additional metrics summary
    output_file.write("\nReward Info Aggregates:\n")
    for key, metrics in reward_info_aggregates.items():
        avg_value = metrics['total'] / metrics['count'] if metrics['count'] > 0 else 0
        output_file.write(f"{key}: Average = {avg_value}\n")

    output_file.write("=" * 50 + "\n")

    # New section for bucketed results
    output_file.write("Bucketed Results\n")
    output_file.write("=" * 50 + "\n")
    buckets = [(0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5), 
               (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1), (1, 1.1)]
    for lower, upper in buckets:
        bucket_sessions = [
            session for session in all_sessions 
            if 'session_score' in session and session['session_score'] and lower <= float(session['session_score']) < upper
        ]
        if bucket_sessions:
            avg_time = mean(float(session.get('duration', 0)) for session in bucket_sessions)
            avg_steps = mean(int(session.get('navigation_steps', 0)) for session in bucket_sessions)
            avg_score = mean(float(session.get('session_score', 0)) for session in bucket_sessions if session.get('session_score'))
            avg_cost = mean(session.get('session_cost', 0.0) for session in bucket_sessions)
            avg_tokens = mean(session.get('session_tokens', 0) for session in bucket_sessions)
            output_file.write(f"Bucket {lower} - {upper}:\n")
            output_file.write(f"  Number of Sessions: {len(bucket_sessions)}\n")
            output_file.write(f"  Average Time: {avg_time}\n")
            output_file.write(f"  Average Steps: {avg_steps}\n")
            output_file.write(f"  Average Score: {avg_score}\n")
            output_file.write(f"  Average Cost: {avg_cost} cents\n")
            output_file.write(f"  Average Tokens: {avg_tokens}\n")
            output_file.write("  Page Visits:\n")
            bucket_page_visits = defaultdict(lambda: {'all': 0, 'completed': 0, 'timeout': 0})
            for session in bucket_sessions:
                for page, visits in session.get('session_page_visits', {}).items():
                    bucket_page_visits[page]['all'] += visits
                    termination_reason = session.get('session_termination_reason', 'unknown')
                    if termination_reason == 'completed':
                        bucket_page_visits[page]['completed'] += visits
                    elif termination_reason == 'timeout':
                        bucket_page_visits[page]['timeout'] += visits
            for page, counts in bucket_page_visits.items():
                output_file.write(f"    {page}: All: {counts['all']}, Completed: {counts['completed']}, Timeout: {counts['timeout']}\n")
            
            # Aggregate reward_info for the bucket

            observer_logs_dir = 'analytics_script/observer_logs'


            bucket_reward_info_aggregates = defaultdict(lambda: {'total': 0.0, 'count': 0})
            for session in bucket_sessions:
                session_id = session['session_id']
                log_file_path = os.path.join(observer_logs_dir, f"{session_id}.jsonl")
                if os.path.exists(log_file_path):
                    log_contents = read_jsonl(log_file_path)
                    for log in log_contents:
                        reward_info = log.get('reward_info', {})
                        for key, value in reward_info.items():
                            if isinstance(value, (int, float)):
                                bucket_reward_info_aggregates[key]['total'] += value
                                bucket_reward_info_aggregates[key]['count'] += 1
            output_file.write("  Reward Info Aggregates:\n")
            for key, metrics in bucket_reward_info_aggregates.items():
                avg_value = metrics['total'] / metrics['count'] if metrics['count'] > 0 else 0
                output_file.write(f"    {key}: Average = {avg_value}\n")
            output_file.write("\n")
    output_file.write("=" * 50 + "\n")

def main():
    session_details_file = 'analytics_script/observer_logs/session_details.csv'
    observer_logs_dir = 'analytics_script/observer_logs'
    portkey_csv_file = 'analytics_script/observer_logs/portkey.csv'
    config_used_file = 'analytics_script/observer_logs/config_used'

    session_details = read_csv(session_details_file)
    
    # Check if portkey.csv exists
    if os.path.exists(portkey_csv_file):
        portkey_data = read_csv(portkey_csv_file)
    else:
        portkey_data = []  # Initialize to empty list if file doesn't exist
    
    with open('analytics_script/report.txt', 'w') as output_file:
        all_sessions, completed_sessions, timeout_sessions, page_visits, total_tokens, total_cost, total_time, reward_info_aggregates = process_sessions(
            session_details, observer_logs_dir, portkey_data, output_file
        )
        print_summary(
            all_sessions, completed_sessions, timeout_sessions, page_visits, 
            total_tokens, total_cost, total_time, reward_info_aggregates, output_file
        )
        
        # Append config_used to the report
        if os.path.exists(config_used_file):
            with open(config_used_file, 'r') as config_file:
                config_used = config_file.read()
            output_file.write("\n" + "=" * 50 + "\n")
            output_file.write("Config Used\n")
            output_file.write("=" * 50 + "\n")
            output_file.write(config_used + "\n")
            output_file.write("=" * 50 + "\n")

if __name__ == "__main__":
    main()