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