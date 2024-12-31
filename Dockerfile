# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add watchdog for auto-reloading
RUN pip install watchdog

# Set environment variable for Gradio port
ENV GRADIO_SERVER_PORT=7860

# Command to run the application with auto-reload
CMD ["python", "-m", "watchdog.watchmedo", "auto-restart", "--directory", ".", "--pattern", "*.py", "--recursive", "--", "python", "app.py"]