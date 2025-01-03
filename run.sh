#!/bin/bash

PORT=7860
DEBUG=0
DEBUG_PORT=5678

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            DEBUG=1
            shift
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# Kill any process using our ports
echo "Checking if ports are in use..."
for p in $PORT $DEBUG_PORT; do
    if lsof -i :$p > /dev/null; then
        echo "Killing process on port $p..."
        lsof -ti :$p | xargs kill -9
    fi
done

# Stop any running gradio-app container
echo "Stopping any running gradio-app containers..."
docker ps -q --filter ancestor=gradio-app | xargs -r docker stop

# Remove any stopped containers
echo "Removing stopped containers..."
docker ps -a -q --filter ancestor=gradio-app | xargs -r docker rm

# Build the new image
echo "Building new Docker image..."
docker build -t gradio-app .

# Run the new container with volume mount
echo "Starting new container with volume mount..."
if [ $DEBUG -eq 1 ]; then
    echo "Running in debug mode on port $DEBUG_PORT..."
    docker run -p $PORT:$PORT \
        -p $DEBUG_PORT:$DEBUG_PORT \
        -v "$(pwd):/app" \
        -e PYTHONUNBUFFERED=1 \
        -e DEBUG=1 \
        --name gradio-app \
        gradio-app python -m debugpy --listen 0.0.0.0:$DEBUG_PORT --wait-for-client app.py
else
    docker run -p $PORT:$PORT \
        -v "$(pwd):/app" \
        --name gradio-app \
        gradio-app
fi