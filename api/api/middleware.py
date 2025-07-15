from django.db import close_old_connections
import logging
from django.http import JsonResponse
from django.db import OperationalError

logger = logging.getLogger(__name__)

class CloseDBConnectionsMiddleware:
    """
    Middleware to ensure old DB connections are closed after each request.
    This helps prevent connection leaks and exhaustion under high load.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        close_old_connections()
        return response

class DatabaseOptimizationMiddleware:
    """
    Middleware to handle database optimization issues gracefully
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, OperationalError):
            error_msg = str(exception).lower()
            
            # Handle temp file limit exceeded
            if 'temp_file_limit' in error_msg:
                logger.error(f"Database temp file limit exceeded for {request.path}: {exception}")
                return JsonResponse({
                    'error': 'Query too complex. Please try again with more specific filters.',
                    'code': 'QUERY_TOO_LARGE'
                }, status=503)
            
            # Handle other database operational errors
            if any(phrase in error_msg for phrase in ['connection', 'timeout', 'server closed']):
                logger.error(f"Database connection error for {request.path}: {exception}")
                return JsonResponse({
                    'error': 'Database temporarily unavailable. Please try again.',
                    'code': 'DATABASE_UNAVAILABLE'
                }, status=503)
        
        return None
