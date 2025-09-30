#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Drop and recreate database
python manage.py flush --noinput

# Run migrations
python manage.py migrate

# Seed data (includes users)
python manage.py seed_data

echo "Build completed successfully!"
