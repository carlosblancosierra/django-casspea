#!/bin/bash

# Variables
IMAGE_NAME="django-casspea"
REGISTRY_URL="071222593443.dkr.ecr.eu-west-2.amazonaws.com"
EC2_USER="ubuntu"
EC2_IP="18.135.11.8"
KEY_PATH="~/.ssh/django-casspea.pem"

# Step 1: Commit changes
echo "Committing changes..."
git add .
git commit -m "Updated fixture loading command to skip non-empty models"

# Step 2: Build Docker image
echo "Building Docker image..."
docker build -t $IMAGE_NAME:web .
docker build -t $IMAGE_NAME:nginx-proxy ./nginx

# Step 3: Push Docker image to registry
echo "Pushing Docker image to registry..."
docker tag $IMAGE_NAME:web $REGISTRY_URL/$IMAGE_NAME:web
docker tag $IMAGE_NAME:nginx-proxy $REGISTRY_URL/$IMAGE_NAME:nginx-proxy
docker push $REGISTRY_URL/$IMAGE_NAME:web
docker push $REGISTRY_URL/$IMAGE_NAME:nginx-proxy

# Step 4: SSH into EC2 instance and deploy
echo "Deploying to EC2 instance..."
ssh -i $KEY_PATH $EC2_USER@$EC2_IP << EOF
    cd ~/django-casspea

    # Pull the new Docker images
    echo "Pulling the latest Docker images..."
    docker pull $REGISTRY_URL/$IMAGE_NAME:web
    docker pull $REGISTRY_URL/$IMAGE_NAME:nginx-proxy

    # Stop and remove existing containers
    echo "Stopping and removing existing containers..."
    docker-compose -f docker-compose.staging.yml down --remove-orphans

    # Start new containers
    echo "Starting new containers..."
    docker-compose -f docker-compose.staging.yml up -d

    # Verify the deployment
    echo "Verifying the deployment..."
    curl http://$EC2_IP
EOF

echo "Deployment completed!"
