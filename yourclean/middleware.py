"""
CORS middleware для Django (простая версия без django-cors-headers)
"""
import os
from django.http import JsonResponse
from django.conf import settings


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = JsonResponse({})
            origin = request.META.get('HTTP_ORIGIN', '')
            allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
            
            if allowed_origins and origin in allowed_origins:
                response['Access-Control-Allow-Origin'] = origin
            elif allowed_origins:
                response['Access-Control-Allow-Origin'] = allowed_origins[0]
            else:
                response['Access-Control-Allow-Origin'] = origin or '*'
            
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Max-Age'] = '86400'
            return response

        response = self.get_response(request)

        # Add CORS headers to all responses
        origin = request.META.get('HTTP_ORIGIN', '')
        allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        
        if allowed_origins and origin in allowed_origins:
            response['Access-Control-Allow-Origin'] = origin
        elif allowed_origins:
            response['Access-Control-Allow-Origin'] = allowed_origins[0]
        else:
            # В продакшене можно разрешить все, но лучше указать конкретные домены
            response['Access-Control-Allow-Origin'] = origin or '*'
        
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'

        return response

