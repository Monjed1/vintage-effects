#!/bin/bash

# Vintage Video Effects API deployment script
echo "Deploying Vintage Video Effects API..."

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null
then
    echo "Gunicorn not found. Installing..."
    pip install gunicorn
fi

# Create necessary directories
mkdir -p temp_videos
mkdir -p output_videos
mkdir -p logs

# Set the base URL for the server - replace this with your actual domain or IP
# This is used for generating URLs to processed videos
export SERVER_HOST="0.0.0.0"
export SERVER_PORT="5557"
export SERVER_BASE_URL="http://62.171.168.74:5557"

# Start server with gunicorn
echo "Starting server on port 5557..."
nohup gunicorn --bind 0.0.0.0:5557 --workers 4 app:app > logs/vintage_effects.log 2>&1 &

# Check if server started
sleep 2
if pgrep -f "gunicorn.*app:app" > /dev/null
then
    echo "Server started successfully on port 5557."
    echo "API is accessible at: http://62.171.168.74:5557"
    echo "Visit /api/effects to get a list of available effects."
    echo "Use /api/url/apply-effect and /api/url/combine-effects for URL-based processing."
else
    echo "Failed to start server. Check logs/vintage_effects.log for details."
fi 