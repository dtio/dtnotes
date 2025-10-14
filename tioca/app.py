# app.py
from flask import Flask
import os

# Initialize the Flask application
app = Flask(__name__)

# Define a simple environment variable to show where the app is running
# This helps confirm the container is using the correct configuration
GREETING = os.environ.get("GREETING", "Hello, Container!")

@app.route('/')
def home():
    """
    The main route, which returns a greeting message.
    """
    return f"<h1>{GREETING}</h1><p>This Flask app is running successfully inside a Docker container, served by Gunicorn!</p>"

# Note: We do not run app.run() here. 
# Gunicorn will handle starting the application using the 'app' object.
# The command in the Dockerfile will be 'gunicorn app:app'.
