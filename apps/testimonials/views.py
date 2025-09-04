from rest_framework import generics, permissions
from .models import Testimonial
from .serializers import TestimonialSerializer

class TestimonialCreateView(generics.CreateAPIView):
    """
    API endpoint for users to submit a new testimonial.
    The user must be authenticated to submit.
    """
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Assign the current user as the testimonial author
        serializer.save(user=self.request.user)

class PublishedTestimonialListView(generics.ListAPIView):
    """
    API endpoint to retrieve all published testimonials.
    This endpoint is public and does not require authentication.
    """
    queryset = Testimonial.objects.filter(is_published=True)
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.AllowAny]
