import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.environ.get('NFIG_API_KEY')

def create_workflow(goal):
    url = "https://api-staging.nfig.ai/external-apis/request/workflow/autonomous/create"
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
    else:
        print(f"Failed to create workflow: {response.status_code} - {response.text}")
    return None

def run_workflow(workflow_id):
    url = "https://api-staging.nfig.ai/external-apis/request/workflow/autonomous/run"
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
    else:
        print(f"Failed to run workflow: {response.status_code} - {response.text}")
    return None

if __name__ == "__main__":
    goal = "go to https://webshop.nfig.ai/abc which is an ecommerce website, Follow the instruction on screen,& complete the purchase, Make sure that all respective choices of the product specification are chosen in product details page. view a product details click on the product ID."
    workflow_id = create_workflow(goal)
    if workflow_id:
        print(f"Workflow created successfully with ID: {workflow_id}")
        session_id = run_workflow(workflow_id)
        if session_id:
            print(f"Workflow run successfully with session ID: {session_id}")
        else:
            print("Failed to run workflow.")
    else:
        print("Failed to create workflow.")