from flask import Flask, jsonify, request
import threading
import time
import os
import shutil

app = Flask(__name__)

# Global variables for observer state
observer_running = False
observer_thread = None
log_directory = "user_session_logs/mturk"

def observer_task(start, end):
    """
    Function to simulate log monitoring.
    It processes session IDs from start to end.
    """
    global observer_running
    observer_running = True
    session_ids = [f"fixed_{i}" for i in range(start, end + 1)]
    
    for session_id in session_ids:
        if not observer_running:
            break
        print(f"Processing session: {session_id}")
        time.sleep(1)  # Simulate log processing
    observer_running = False
    print("Observer task completed.")

@app.route('/start', methods=['POST'])
def start_observer():
    """
    API endpoint to start the observer task.
    It checks if the observer is already running and starts a thread if not.
    """
    global observer_thread, observer_running
    if observer_running:
        return jsonify({"status": "already running"}), 400

    start = int(request.json.get("start", 0))
    end = int(request.json.get("end", 1000))
    observer_thread = threading.Thread(target=observer_task, args=(start, end))
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
    It deletes all files in the specified directory.
    """
    for filename in os.listdir(log_directory):
        file_path = os.path.join(log_directory, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
    return jsonify({"status": "cleaned"}), 200

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
    
    return jsonify({"status": f"session {name} archived", "archive": archive_name}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)