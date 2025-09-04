from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, FAQViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'faqs', FAQViewSet, basename='faq')

urlpatterns = [
    path('', include(router.urls)),
]
