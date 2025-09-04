from django.urls import path
from .views import TestimonialCreateView, PublishedTestimonialListView

app_name = 'testimonials'

urlpatterns = [
    path('create/', TestimonialCreateView.as_view(), name='testimonial-create'),
    path('published/', PublishedTestimonialListView.as_view(), name='testimonial-list-published'),
]
