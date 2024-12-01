#!/bin/bash

# Variables
EC2_USER="ubuntu"
EC2_IP="18.135.11.8"
KEY_PATH="~/.ssh/django-casspea.pem"

echo "Running database migrations..."
ssh -i $KEY_PATH $EC2_USER@$EC2_IP << EOF
    echo "Changing to project directory..."
    cd ~/django-casspea

    echo "Running migrations..."
    docker compose -f docker-compose.prod.yml exec web python manage.py migrate

    echo "Checking migration status..."
    docker compose -f docker-compose.prod.yml exec web python manage.py showmigrations

EOF

echo "Migration completed!"
