# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'Django Backend',
        'debug': settings.DEBUG
    })

@csrf_exempt
def api_data(request):
    """
    API endpoint that returns sample data
    """
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
