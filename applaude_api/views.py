# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

class HealthCheckView(APIView):
    """
    API endpoint for health check
    """
    def get(self, request):
        data = {
            'status': 'healthy',
            'service': 'Django Backend',
            'debug': settings.DEBUG
        }
        return Response(data, status=status.HTTP_200_OK)

class ApiDataView(APIView):
    """
    API endpoint that returns sample data
    """
    def get(self, request):
        data = {
            'message': 'Welcome to Applaude API',
            'data': [
                {'id': 1, 'name': 'Project Alpha', 'status': 'active'},
                {'id': 2, 'name': 'Project Beta', 'status': 'completed'},
                {'id': 3, 'name': 'Project Gamma', 'status': 'pending'}
            ],
            'timestamp': '2024-01-01T00:00:00Z'
        }
        return Response(data, status=status.HTTP_200_OK)

# For backward compatibility, keep function-based views
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check(request):
    if request.method in ['GET', 'OPTIONS']:
        return JsonResponse({
            'status': 'healthy',
            'service': 'Django Backend',
            'debug': settings.DEBUG
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_data(request):
    if request.method in ['GET', 'OPTIONS']:
        data = {
            'message': 'Welcome to Applaude API',
            'data': [
                {'id': 1, 'name': 'Project Alpha', 'status': 'active'},
                {'id': 2, 'name': 'Project Beta', 'status': 'completed'},
                {'id': 3, 'name': 'Project Gamma', 'status': 'pending'}
            ],
            'timestamp': '2024-01-01T00:00:00Z'
        }
        return JsonResponse(data)
    return JsonResponse({'error': 'Method not allowed'}, status=405)
