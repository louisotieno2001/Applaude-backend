from django.urls import path
from .views import InitializePaymentView, PaystackWebhookView, GetLocalizedPricingView

app_name = 'payments'

urlpatterns = [
    path('initialize/', InitializePaymentView.as_view(), name='initialize-payment'),
    path('webhook/', PaystackWebhookView.as_view(), name='paystack-webhook'),
    path('pricing/', GetLocalizedPricingView.as_view(), name='get-pricing'),
]
