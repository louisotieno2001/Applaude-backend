from django.urls import path
from .views import InitializeAPIPaymentView, APIProjectCreateView

app_name = 'api'

urlpatterns = [
    path('initialize-payment/', InitializeAPIPaymentView.as_view(), name='api-initialize-payment'),
    path('projects/create/', APIProjectCreateView.as_view(), name='api-project-create'),
]
