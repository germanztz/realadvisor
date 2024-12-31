#!/bin/bash

PORT=7860

# Kill any process using our port
echo "Checking if port $PORT is in use..."
if lsof -i :$PORT > /dev/null; then
    echo "Killing process on port $PORT..."
    lsof -ti :$PORT | xargs kill -9
fi

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
docker run -p $PORT:$PORT \
    -v "$(pwd):/app" \
    --name gradio-app \
    gradio-app 