#!/bin/bash

# Render Deployment Build Script for Knowledge-ledger Backend
# This script is specifically optimized for Render's deployment environment

set -e  # Exit on any error

echo "🚀 Starting Render Production Build Process..."

# Render automatically sets these environment variables
echo "🔧 Render Environment Variables:"
echo "   PORT: $PORT"
echo "   RENDER: $RENDER"
echo "   RENDER_SERVICE_NAME: $RENDER_SERVICE_NAME"
echo "   RENDER_SERVICE_TYPE: $RENDER_SERVICE_TYPE"

echo "📦 Installing Production Dependencies..."
pip install -r requirements.txt

echo "🔧 Making migrations..."
python manage.py makemigrations --no-input

echo "🔧 Running Database Migrations..."
python manage.py migrate --no-input

echo "📁 Collecting Static Files for Render..."
echo "   📂 Current directory: $(pwd)"
echo "   📂 Django settings module: $DJANGO_SETTINGS_MODULE"
echo "   📂 Static files directory: $(python -c 'from django.conf import settings; print(settings.STATIC_ROOT)')"

# Check if whitenoise is available
echo "   🔍 Checking Whitenoise availability..."
if python -c "import whitenoise; print('Whitenoise available')" 2>/dev/null; then
    echo "   ✅ Whitenoise package is available"
else
    echo "   ❌ Whitenoise package not available - static files may not serve properly"
fi

# Force static file collection with verbose output
python manage.py collectstatic --no-input --clear --verbosity=2

# Verify what was collected
echo "   📊 Static files collection results:"
if [ -d "staticfiles" ]; then
    echo "   ✅ staticfiles directory exists"
    echo "   📁 Contents:"
    ls -la staticfiles/ | head -10
    echo "   📊 Total files: $(find staticfiles/ -type f | wc -l)"
    
    # Check specifically for drf-yasg
    if [ -d "staticfiles/drf-yasg" ]; then
        echo "   ✅ drf-yasg static files found"
        ls -la staticfiles/drf-yasg/ | head -5
    else
        echo "   ❌ drf-yasg static files missing"
        echo "   🔍 Checking what's in staticfiles:"
        find staticfiles/ -type d | head -10
        
        # Try to manually find and copy drf-yasg static files
        echo "   🔧 Attempting manual drf-yasg static file copy..."
        if python -c "import drf_yasg; print('drf-yasg available')" 2>/dev/null; then
            echo "   📁 drf-yasg package is available"
            DRF_YASG_PATH=$(python -c "import drf_yasg; print(drf_yasg.__path__[0])" 2>/dev/null)
            if [ -d "$DRF_YASG_PATH/static" ]; then
                echo "   📁 Found drf-yasg static files at: $DRF_YASG_PATH/static"
                cp -r "$DRF_YASG_PATH/static/drf-yasg" staticfiles/ 2>/dev/null && echo "   ✅ Manual copy successful" || echo "   ❌ Manual copy failed"
            else
                echo "   ❌ No static directory in drf-yasg package"
            fi
        else
            echo "   ❌ drf-yasg package not available"
        fi
    fi
    
    # Check whitenoise configuration
    echo "   🔍 Verifying Whitenoise configuration..."
    if python -c "from django.conf import settings; print('WHITENOISE_USE_FINDERS:', getattr(settings, 'WHITENOISE_USE_FINDERS', 'Not set'))" 2>/dev/null; then
        echo "   ✅ Whitenoise settings verified"
    else
        echo "   ⚠️  Could not verify Whitenoise settings"
    fi
else
    echo "   ❌ staticfiles directory not created"
    echo "   🔍 Checking current directory:"
    ls -la
fi

echo "🔍 Running Production Security Checks..."
python manage.py check --deploy

echo "🧹 Cleaning up temporary files..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete

echo "📊 Render Build Summary:"
echo "   ✅ Dependencies installed"
echo "   ✅ Database migrated"
echo "   ✅ Static files collected"
echo "   ✅ Security checks passed"
echo "   ✅ Cache cleared"

echo "🎉 Render Build Complete!"
echo "🚀 Your Django app is ready for Render deployment!"

if [[ $CREATE_SUPERUSER == "True" ]]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --no-input
    echo "✅ Superuser created successfully!"
fi

echo "💡 Render Deployment Notes:"
echo "   1. Static files are collected in 'staticfiles' directory"
echo "   2. Database migrations are automatically applied"
echo "   3. Gunicorn will start on port $PORT"
echo "   4. Environment variables are set via Render dashboard"
echo "   5. SSL is automatically handled by Render"
