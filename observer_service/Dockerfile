# observer_service/Dockerfile

# Start with a Python base image
FROM python:3.8-slim

# Set the working directory
WORKDIR /observer

# Copy the observer script to the working directory
COPY . .

# Install necessary Python packages
RUN pip install -r requirements.txt

# Start the observer script
CMD ["python", "-u", "observer_script.py"]
