#!/bin/bash

# Make migrations first
echo "Making migrations..."
python manage.py makemigrations

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Wait a moment for migrations to complete
sleep 2

# Check if categories exist before loading
if ! python manage.py dumpdata products.ProductCategory | grep -q "model"; then
    echo "Loading initial categories..."
    python manage.py loaddata initial_categories
else
    echo "Categories already exist, skipping..."
fi

# Check if products exist before loading
if ! python manage.py dumpdata products.Product | grep -q "model"; then
    echo "Loading initial products..."
    python manage.py loaddata initial_products
else
    echo "Products already exist, skipping..."
fi

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
