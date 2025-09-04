from django.http import JsonResponse

def health_check(request):
    """
    Simple health check endpoint for Elastic Beanstalk.
    """
    return JsonResponse({"status": "ok"})
