# Use an official Python runtime as the base image
FROM python:3.14.2-slim-trixie

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # build-essential \
    # libglib2.0-0 \
    # libnss3 \
    # libgconf-2-4 \
    # libfontconfig1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
# COPY requirements.txt .
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Gradio port and Python path
# ENV GRADIO_SERVER_PORT=7860
# ENV PYTHONPATH=/app

# Command to run the application with auto-reload
# CMD ["python", "-m", "watchdog.watchmedo", "auto-restart", "--directory", ".", "--pattern", "*.py", "--recursive", "--", "python", "app.py"]
CMD ["python","src/daemon.py","--run"]