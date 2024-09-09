import requests
import time

# Function to create a log export
def create_log_export(api_key, workspace_id, trace_id):
    url = "https://api.portkey.ai/v1/logs/exports"
    headers = {
        "x-portkey-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "workspace_id": workspace_id,
        "filters": {
            "trace_id": trace_id
        },
        "requested_data": ["traceID", "span_name"]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Function to start a log export
def start_log_export(api_key, export_id):
    url = f"https://api.portkey.ai/v1/logs/exports/{export_id}/start"
    headers = {
        "x-portkey-api-key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers)
    return response.json()

# Function to download a log export
def download_log_export(api_key, export_id):
    url = f"https://api.portkey.ai/v1/logs/exports/{export_id}/download"
    headers = {
        "x-portkey-api-key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Function to fetch and print data for a list of trace IDs
def fetch_and_print_trace_data(api_key, workspace_id, trace_ids):
    for trace_id in trace_ids:
        print(f"Fetching data for Trace ID: {trace_id}")
        
        # Create log export
        export_info = create_log_export(api_key, workspace_id, trace_id)
        print(export_info)
        export_id = export_info['id']
        
        # Start log export
        start_log_export(api_key, export_id)
        
        # Wait for the export to be ready
        time.sleep(5)
        
        # Download log export
        portkey_info = download_log_export(api_key, export_id)
        
        # Print the fetched data
        print(f"Portkey Info for Trace ID {trace_id}:")
        print(portkey_info)
        print("-" * 50)

# Main function
def main():
    portkey_api_key = 'uKxEwJJFQax+OdewHyy/BZ9wml2q'  # Replace with your actual Portkey API key
    workspace_id = '4c2e148e-1e58-4790-b42d-fdbb78f17248'  # Replace with your actual workspace ID
    trace_ids = ['81c4df54-7fd0-4c32-99d7-6606fc2edc8e', '95c2d706-b304-4f23-9d53-65fc10f4e295', '6d4ca9a4-c55b-4b00-951d-b8476c072649']  # Replace with your actual trace IDs

    fetch_and_print_trace_data(portkey_api_key, workspace_id, trace_ids)

if __name__ == "__main__":
    main()