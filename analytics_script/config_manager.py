import json
import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('NFIG_API_KEY')
LOGIN_URL = 'https://api-staging.nfig.ai/auth/login'
SET_CONFIG_URL = 'https://api-staging.nfig.ai/workflows/org/config/save'

def fetch_current_config():
    url = 'http://api-staging.nfig.ai/external-apis/request/org/config'
    headers = {'api-key': API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def print_current_config(output_file):
    config = fetch_current_config()
    with open(output_file, 'w') as config_file:
        config_file.write("=" * 50 + "\n")
        config_file.write("Current Config Used\n")
        config_file.write("=" * 50 + "\n")
        config_file.write(json.dumps(config, indent=4) + "\n")
        config_file.write("=" * 50 + "\n")

def login(email, password):
    response = requests.post(LOGIN_URL, json={'email': email, 'password': password})
    response.raise_for_status()
    return response.json()['token']

def set_new_config(token, config_file):
    with open(config_file, 'r') as file:
        config_data = json.load(file)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.post(SET_CONFIG_URL, headers=headers, json=config_data)
    response.raise_for_status()
    return response.json()

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == 'fetch':
            print_current_config('analytics_script/config_used')
        elif sys.argv[1] == 'set':
            email = input("Enter email: ")
            password = input("Enter password: ")
            token = login(email, password)
            set_new_config(token, 'config_to_set.json')
        return

    while True:
        print("1. Fetch Current Config")
        print("2. Set New Config")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            print_current_config('analytics_script/config_used')
        elif choice == '2':
            email = input("Enter email: ")
            password = input("Enter password: ")
            token = login(email, password)
            set_new_config(token, 'config_to_set.json')
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()