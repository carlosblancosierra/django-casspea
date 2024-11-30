#!/bin/bash

# Script to connect to the live logs on the web app

# Variables
IMAGE_NAME="django-casspea"
REGISTRY_URL="071222593443.dkr.ecr.eu-west-2.amazonaws.com"
EC2_USER="ubuntu"
EC2_IP="18.135.11.8"
KEY_PATH="$HOME/.ssh/django-casspea.pem"
PROJECT_DIR="/home/ubuntu/django-casspea"

# Function to display usage
usage() {
    echo "Usage: $0 [service_name]"
    echo "If no service_name is provided, logs for all services will be streamed."
    echo "Example: $0 web"
    exit 1
}

# Check for help flag
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
fi

# Assign service name if provided
SERVICE=$1

# Construct Docker logs command
if [ -z "$SERVICE" ]; then
    LOG_COMMAND="docker-compose -f docker-compose.prod.yml logs -f"
else
    LOG_COMMAND="docker-compose -f docker-compose.prod.yml logs -f $SERVICE"
fi

# Connect to EC2 and stream logs
ssh -i "$KEY_PATH" "$EC2_USER@$EC2_IP" << EOF
    echo "Connecting to EC2 instance at $EC2_IP..."
    cd "$PROJECT_DIR" || { echo "Project directory not found."; exit 1; }
    echo "Streaming logs..."
    $LOG_COMMAND
EOF
