#!/bin/bash

echo "infer.sh is running"

# Load configuration values from config.yaml
eval $(python3 /config/config.py)

echo "APP_HOST: $APP_HOST"
echo "APP_PORT: $APP_PORT"

# Run the uvicorn server with the extracted configuration
uvicorn main:app --reload --host $APP_HOST --port $APP_PORT

