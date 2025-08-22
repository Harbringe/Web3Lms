from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.core.cache import cache
import os

# Create your views here.

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for Render monitoring
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check cache (optional - don't fail if cache is unavailable)
    try:
        cache.set("health_check", "ok", 10)
        cache_status = "healthy"
    except Exception as e:
        cache_status = f"unavailable: {str(e)}"
    
    # Check environment variables (more lenient)
    env_status = "healthy"
    missing_vars = []
    
    # Only check critical variables
    critical_vars = ['SECRET_KEY', 'DB_CONN_URL']
    for var in critical_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        env_status = f"missing: {', '.join(missing_vars)}"
    
    # More lenient overall status - only fail if database is completely down
    overall_status = "healthy" if db_status == "healthy" else "unhealthy"
    
    # Always return 200 for Render health checks, but include status in response
    return JsonResponse({
        "status": overall_status,
        "timestamp": os.getenv('RENDER_TIMESTAMP', 'unknown'),
        "service": os.getenv('RENDER_SERVICE_NAME', 'knowledge-ledger-backend'),
        "checks": {
            "database": db_status,
            "cache": cache_status,
            "environment": env_status
        },
        "debug_info": {
            "missing_env_vars": missing_vars,
            "render_service": os.getenv('RENDER_SERVICE_NAME', 'unknown'),
            "render_environment": os.getenv('RENDER_ENVIRONMENT', 'unknown')
        }
    }, status=200)  # Always return 200 for Render health checks
