#!/bin/bash

# Production Build Script for Knowledge-ledger Backend
# This script sets up the production environment and builds the application

set -e  # Exit on any error

echo "🚀 Starting Production Build Process..."

# Set production environment
export DJANGO_SETTINGS_MODULE=backend.settings
export DJANGO_ENV=production

echo "📦 Installing Production Dependencies..."
pip install -r requirements.txt

echo "🔒 Setting Production Environment Variables..."
# Ensure DEBUG is set to False for production
export DEBUG=False
# Set RENDER environment variable for logging configuration
export RENDER=True

echo "📁 Creating necessary directories..."
# Create logs directory for Django logging
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

echo "🗄️  Running Database Migrations..."
python manage.py migrate --no-input

echo "📁 Collecting Static Files for Production..."
python manage.py collectstatic --no-input --clear

echo "🔍 Running Production Security Checks..."
python manage.py check --deploy

echo "🧹 Cleaning up temporary files..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

echo "📊 Production Build Summary:"
echo "   ✅ Dependencies installed"
echo "   ✅ Logs directory created"
echo "   ✅ Database migrated"
echo "   ✅ Static files collected"
echo "   ✅ Security checks passed"
echo "   ✅ Cache cleared"

echo "🎉 Production Build Complete!"
echo "🚀 Your Django app is ready for production deployment!"

# Optional: Create superuser if environment variable is set
if [[ $CREATE_SUPERUSER == "True" ]]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --no-input
    echo "✅ Superuser created successfully!"
fi

echo "💡 Next steps:"
echo "   1. Ensure your .env file has all production values"
echo "   2. Set DEBUG=False in your environment"
echo "   3. Configure your production database"
echo "   4. Set up your production web server (gunicorn, uwsgi, etc.)"
echo "   5. Configure your reverse proxy (nginx, etc.)"