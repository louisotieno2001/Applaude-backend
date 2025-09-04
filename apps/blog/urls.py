from django.urls import path
from .views import BlogPostListCreateView, BlogPostRetrieveUpdateDestroyView

app_name = 'blog'

urlpatterns = [
    path('', BlogPostListCreateView.as_view(), name='blogpost-list-create'),
    path('<int:pk>/', BlogPostRetrieveUpdateDestroyView.as_view(), name='blogpost-detail'),
]
