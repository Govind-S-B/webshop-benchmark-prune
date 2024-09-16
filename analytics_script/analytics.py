import sqlite3
from collections import defaultdict
from statistics import mean
import json
import os

def initialize_report(file_path):
    """Initialize the report file with a header."""
    with open(file_path, 'w') as report:
        report.write("=" * 50 + "\n")
        report.write("Analytics Report\n")
        report.write("=" * 50 + "\n\n")

def append_to_report(file_path, content):
    """Append content to the report file."""
    with open(file_path, 'a') as report:
        report.write(content + "\n")

def fetch_sessions(conn):
    """Fetch all sessions from the database."""
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions')
    columns = [description[0] for description in cursor.description]
    sessions = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return sessions

def compute_summary_statistics(sessions):
    """Compute summary statistics from sessions."""
    all_sessions = sessions
    completed_sessions = [s for s in sessions if s['session_termination_reason'] == 'completed']
    timeout_sessions = [s for s in sessions if s['session_termination_reason'] == 'timeout']
    
    total_tokens = sum(s.get('session_tokens', 0) for s in sessions)
    total_cost = sum(s.get('session_cost', 0.0) for s in sessions)
    total_time = sum(s.get('duration', 0.0) for s in sessions)
    
    summary = {
        'Total Sessions': len(all_sessions),
        'Completed Sessions': len(completed_sessions),
        'Timeout Sessions': len(timeout_sessions),
        'Total Tokens Used': total_tokens,
        'Total Cost': total_cost,
        'Total Time (seconds)': total_time
    }
    
    if timeout_sessions:
        summary['Average Steps in Timeout Sessions'] = mean(s.get('navigation_steps', 0) for s in timeout_sessions)
        summary['Average Cost in Timeout Sessions'] = mean(s.get('session_cost', 0.0) for s in timeout_sessions)
        summary['Average Tokens in Timeout Sessions'] = mean(s.get('session_tokens', 0) for s in timeout_sessions)
    else:
        summary['Average Steps in Timeout Sessions'] = 0
        summary['Average Cost in Timeout Sessions'] = 0.0
        summary['Average Tokens in Timeout Sessions'] = 0
    
    if completed_sessions:
        summary['Average Time in Completed Sessions'] = mean(s.get('duration', 0.0) for s in completed_sessions)
        summary['Average Steps in Completed Sessions'] = mean(s.get('navigation_steps', 0) for s in completed_sessions)
        summary['Average Score in Completed Sessions'] = mean(s.get('session_score', 0.0) for s in completed_sessions)
        summary['Average Cost in Completed Sessions'] = mean(s.get('session_cost', 0.0) for s in completed_sessions)
        summary['Average Tokens in Completed Sessions'] = mean(s.get('session_tokens', 0) for s in completed_sessions)
        
        success_sessions = [s for s in completed_sessions if s.get('session_score', 0.0) == 1.0]
        summary['Success Ratio (All Sessions)'] = len(success_sessions) / len(all_sessions) if all_sessions else 0
        summary['Success Ratio (Completed Sessions)'] = len(success_sessions) / len(completed_sessions) if completed_sessions else 0
    else:
        summary['Average Time in Completed Sessions'] = 0.0
        summary['Average Steps in Completed Sessions'] = 0
        summary['Average Score in Completed Sessions'] = 0.0
        summary['Average Cost in Completed Sessions'] = 0.0
        summary['Average Tokens in Completed Sessions'] = 0
        summary['Success Ratio (All Sessions)'] = 0
        summary['Success Ratio (Completed Sessions)'] = 0
    
    return summary, completed_sessions, timeout_sessions

def compute_page_visits(sessions):
    """Compute page visit statistics."""
    page_visits = defaultdict(lambda: {'All Visits': 0, 'Completed Visits': 0, 'Timeout Visits': 0})
    
    for session in sessions:
        for page in ['count_page_index', 'count_page_search_results', 'count_page_item_page', 'count_page_item_sub_page', 'count_page_done']:
            count = session.get(page, 0)
            page_name = page.replace('count_page_', '')
            page_visits[page_name]['All Visits'] += count
            if session['session_termination_reason'] == 'completed':
                page_visits[page_name]['Completed Visits'] += count
            elif session['session_termination_reason'] == 'timeout':
                page_visits[page_name]['Timeout Visits'] += count
    
    return page_visits

def compute_bucketed_results(sessions):
    """Compute bucketed results based on session_score."""
    buckets = [(0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5),
               (0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]
    bucketed_results = []
    
    for lower, upper in buckets:
        bucket_sessions = [s for s in sessions if s.get('session_score') is not None and lower <= float(s['session_score']) < upper]
        if bucket_sessions:
            avg_time = mean(s.get('duration', 0.0) for s in bucket_sessions)
            avg_steps = mean(s.get('navigation_steps', 0) for s in bucket_sessions)
            avg_score = mean(float(s.get('session_score', 0.0)) for s in bucket_sessions)
            avg_cost = mean(s.get('session_cost', 0.0) for s in bucket_sessions)
            avg_tokens = mean(s.get('session_tokens', 0) for s in bucket_sessions)
            
            bucketed_results.append({
                'Bucket Range': f"{lower} - {upper}",
                'Number of Sessions': len(bucket_sessions),
                'Average Time (seconds)': avg_time,
                'Average Steps': avg_steps,
                'Average Score': avg_score,
                'Average Cost (cents)': avg_cost,
                'Average Tokens': avg_tokens
            })
    
    return bucketed_results

def fetch_config_used(config_path):
    """Fetch configuration used from the configuration file."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config_used = config_file.read()
        return config_used
    else:
        return "No configuration file found."

def generate_report(report_path, summary, page_visits, bucketed_results, config_used):
    """Generate the report.txt file with all analytics."""
    initialize_report(report_path)
    
    # Write Summary Statistics
    append_to_report(report_path, "="*50)
    append_to_report(report_path, "Summary Statistics")
    append_to_report(report_path, "="*50 + "\n")
    for key, value in summary.items():
        append_to_report(report_path, f"{key}: {value}")
    append_to_report(report_path, "\n")
    
    # Write Page Visits
    append_to_report(report_path, "="*50)
    append_to_report(report_path, "Page Visits")
    append_to_report(report_path, "="*50 + "\n")
    for page, counts in page_visits.items():
        append_to_report(report_path, f"Page: {page}")
        for count_key, count_value in counts.items():
            append_to_report(report_path, f"  {count_key}: {count_value}")
        append_to_report(report_path, "")
    append_to_report(report_path, "\n")
    
    # Write Bucketed Results
    append_to_report(report_path, "="*50)
    append_to_report(report_path, "Bucketed Results")
    append_to_report(report_path, "="*50 + "\n")
    for bucket in bucketed_results:
        append_to_report(report_path, f"Bucket Range: {bucket['Bucket Range']}")
        append_to_report(report_path, f"  Number of Sessions: {bucket['Number of Sessions']}")
        append_to_report(report_path, f"  Average Time (seconds): {bucket['Average Time (seconds)']}")
        append_to_report(report_path, f"  Average Steps: {bucket['Average Steps']}")
        append_to_report(report_path, f"  Average Score: {bucket['Average Score']}")
        append_to_report(report_path, f"  Average Cost (cents): {bucket['Average Cost (cents)']}")
        append_to_report(report_path, f"  Average Tokens: {bucket['Average Tokens']}")
        append_to_report(report_path, "")
    append_to_report(report_path, "\n")
    
    # Write Configurations Used
    append_to_report(report_path, "="*50)
    append_to_report(report_path, "Configurations Used")
    append_to_report(report_path, "="*50 + "\n")
    append_to_report(report_path, config_used)
    append_to_report(report_path, "="*50 + "\n")

def main():
    db_path = 'analytics_script/analytics.db'
    report_path = 'analytics_script/report.txt'
    config_used_file = 'analytics_script/config_used.json'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} does not exist.")
        return
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Fetch all sessions
    sessions = fetch_sessions(conn)
    
    # Compute summary statistics
    summary, completed_sessions, timeout_sessions = compute_summary_statistics(sessions)
    
    # Compute page visits
    page_visits = compute_page_visits(sessions)
    
    # Compute bucketed results
    bucketed_results = compute_bucketed_results(sessions)
    
    # Fetch configurations used from file
    config_used = fetch_config_used(config_used_file)
    
    # Generate the report
    generate_report(report_path, summary, page_visits, bucketed_results, config_used)
    
    # Close the database connection
    conn.close()
    
    print(f"Report generated successfully at {report_path}")

if __name__ == "__main__":
    main()