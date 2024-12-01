#!/bin/bash

# Variables
IMAGE_NAME="django-casspea"
REGISTRY_URL="071222593443.dkr.ecr.eu-west-2.amazonaws.com"
EC2_USER="ubuntu"
EC2_IP="18.135.11.8"
KEY_PATH="~/.ssh/django-casspea.pem"
AWS_REGION="eu-west-2"

# Step 0: Login to AWS ECR locally
echo "Logging into AWS ECR locally..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $REGISTRY_URL

# Step 1: Copy necessary files to EC2
echo "Copying configuration files to EC2..."
scp -i $KEY_PATH \
    docker-compose.prod.yml \
    .env.prod \
    .env.prod.proxy-companion \
    $EC2_USER@$EC2_IP:/home/ubuntu/django-casspea/

# Step 2: Build and Push using production docker-compose
echo "Building and pushing Docker images..."
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml push

# Step 3: SSH into EC2 instance and deploy
echo "Deploying to EC2 instance..."
ssh -i $KEY_PATH $EC2_USER@$EC2_IP << EOF
    echo "Changing to project directory..."
    cd ~/django-casspea

    echo "Logging into AWS ECR on EC2..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $REGISTRY_URL

    echo "Pulling latest changes from main branch..."
    git pull origin main

    echo "Stopping existing containers..."
    docker-compose -f docker-compose.prod.yml down --remove-orphans

    echo "Pulling new Docker images..."
    docker pull $REGISTRY_URL/$IMAGE_NAME:web
    docker pull $REGISTRY_URL/$IMAGE_NAME:nginx-proxy

    echo "Starting containers..."
    docker-compose -f docker-compose.prod.yml up -d

    echo "Waiting for web container to be ready..."
    sleep 10

    echo "Running database migrations..."
    docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate

    echo "Checking migration status..."
    docker compose -f docker-compose.prod.yml exec -T web python manage.py showmigrations

    echo "Cleaning up old images..."
    docker image prune -f

    echo "Checking container status..."
    docker ps

    echo "Checking container logs..."
    docker logs django-casspea-web --tail 50
    docker logs nginx-proxy --tail 50
EOF

echo "Deployment completed!"
