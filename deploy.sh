#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Variables
IMAGE_NAME="django-casspea"
REGISTRY_URL="071222593443.dkr.ecr.eu-west-2.amazonaws.com"
EC2_USER="ubuntu"
EC2_IP="18.135.11.8"
KEY_PATH="~/.ssh/django-casspea.pem"
AWS_REGION="eu-west-2"

# Function to log messages with timestamps
log() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $1"
}

# Step 0: Login to AWS ECR locally
log "Logging into AWS ECR locally..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $REGISTRY_URL

# Step 0.1: Clean up local Docker resources to free up space
log "Cleaning up local Docker resources..."
docker system prune -a --volumes -f
log "Local Docker cleanup completed."

# Step 1: Copy necessary files to EC2
log "Copying configuration files to EC2..."
scp -i $KEY_PATH \
    docker-compose.prod.yml \
    .env \
    .env.prod \
    .env.prod.proxy-companion \
    $EC2_USER@$EC2_IP:/home/ubuntu/django-casspea/

# Step 1.1: Export environment variables (optional)
log "Exporting environment variables from .env.prod..."
export $(grep -v '^#' .env.prod | xargs)
log "Environment variables exported."

# Step 2: Build and Push using production docker-compose
log "Building Docker images..."
docker-compose -f docker-compose.prod.yml build
log "Docker images built successfully."

log "Pushing Docker images to ECR..."
docker-compose -f docker-compose.prod.yml push
log "Docker images pushed successfully."

# Step 3: SSH into EC2 instance and deploy
log "Deploying to EC2 instance..."
ssh -i $KEY_PATH $EC2_USER@$EC2_IP << EOF
    set -e

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Changing to project directory..."
    cd ~/django-casspea

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Performing aggressive Docker cleanup..."
    # Stop all running containers
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true

    # Remove all containers
    docker rm -f \$(docker ps -aq) || true

    # Remove all images
    docker rmi -f \$(docker images -aq) || true

    # Remove all volumes
    docker volume rm \$(docker volume ls -q) || true

    # Clean up system
    docker system prune -af --volumes

    # Clean up unused Docker data
    docker builder prune -af

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Checking available disk space..."
    df -h /

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Cleaning up system packages..."
    sudo apt-get clean
    sudo apt-get autoremove -y

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Logging into AWS ECR on EC2..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $REGISTRY_URL

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Pulling latest changes from main branch..."
    git pull origin main

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Pulling new Docker images..."
    docker pull $REGISTRY_URL/$IMAGE_NAME:web
    docker pull $REGISTRY_URL/$IMAGE_NAME:nginx-proxy

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Restoring configuration files..."
    cp -f config_backup/* . 2>/dev/null || true

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Stopping existing containers..."
    docker-compose -f docker-compose.prod.yml down --remove-orphans

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Starting containers..."
    docker-compose -f docker-compose.prod.yml up -d

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Waiting for web container to be ready..."
    sleep 10

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Running database migrations..."
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Checking migration status..."
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py showmigrations

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Cleaning up old Docker images and resources..."
    docker system prune -a --volumes -f
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Docker cleanup on EC2 completed."

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Checking container status..."
    docker ps

    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: Checking container logs..."
    docker logs django-casspea-web --tail 50
    docker logs nginx-proxy --tail 50
EOF

log "Deployment completed!"
