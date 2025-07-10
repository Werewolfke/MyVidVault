from django.db import close_old_connections

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
