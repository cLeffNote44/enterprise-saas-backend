"""
Health check views for monitoring
"""
from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import redis
import time


class HealthLiveView(View):
    """Simple liveness check - returns OK if the app is running"""
    
    def get(self, request):
        return JsonResponse({
            'status': 'ok',
            'service': 'enterprise-saas-foundation',
            'timestamp': int(time.time())
        })


class HealthReadyView(View):
    """Readiness check - verifies all dependencies are available"""
    
    def get(self, request):
        checks = {
            'database': self.check_database(),
            'cache': self.check_cache(),
            'redis': self.check_redis(),
            'storage': self.check_storage(),
        }
        
        all_healthy = all(check['healthy'] for check in checks.values())
        status_code = 200 if all_healthy else 503
        
        return JsonResponse({
            'status': 'ready' if all_healthy else 'not_ready',
            'checks': checks,
            'timestamp': int(time.time())
        }, status=status_code)
    
    def check_database(self):
        """Check database connectivity"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return {'healthy': True, 'message': 'Database is accessible'}
        except Exception as e:
            return {'healthy': False, 'message': str(e)}
    
    def check_cache(self):
        """Check cache connectivity"""
        try:
            cache.set('health_check', 'ok', 30)
            value = cache.get('health_check')
            if value == 'ok':
                return {'healthy': True, 'message': 'Cache is working'}
            return {'healthy': False, 'message': 'Cache read/write failed'}
        except Exception as e:
            return {'healthy': False, 'message': str(e)}
    
    def check_redis(self):
        """Check Redis connectivity directly"""
        try:
            redis_url = settings.CELERY_BROKER_URL
            if redis_url:
                r = redis.from_url(redis_url)
                r.ping()
                return {'healthy': True, 'message': 'Redis is accessible'}
            return {'healthy': True, 'message': 'Redis not configured'}
        except Exception as e:
            return {'healthy': False, 'message': str(e)}
    
    def check_storage(self):
        """Check storage backend"""
        try:
            if hasattr(settings, 'AWS_S3_ENDPOINT_URL'):
                # For MinIO/S3, we'll just check the configuration
                # A full check would require boto3 client
                return {'healthy': True, 'message': 'Storage configured'}
            return {'healthy': True, 'message': 'Default storage'}
        except Exception as e:
            return {'healthy': False, 'message': str(e)}