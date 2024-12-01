#!/bin/bash

# Variables
EC2_USER="ubuntu"
EC2_IP="18.135.11.8"
KEY_PATH="~/.ssh/django-casspea.pem"

echo "Connecting to EC2 and accessing Django container shell..."
ssh -t -i $KEY_PATH $EC2_USER@$EC2_IP "cd ~/django-casspea && docker compose -f docker-compose.prod.yml exec web bash"
