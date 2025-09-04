import os
import requests
import uuid
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .authentication import APIKeyAuthentication
from .models import ApiClient
from .serializers import ApiClientCreateSerializer, APIProjectCreateSerializer
from apps.projects.models import Project
from agents.tasks import run_market_analysis, run_design_analysis
from celery import chain

User = get_user_model()
API_CLIENT_SETUP_FEE = Decimal('99.00') # One-time setup fee for API access

class InitializeAPIPaymentView(generics.CreateAPIView):
    """
    Initializes the payment process for a new API partner.
    Creates a CustomUser and an inactive ApiClient, then initiates payment.
    """
    serializer_class = ApiClientCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if User.objects.filter(email=data['email']).exists():
            return Response({'error': 'An account with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Create a new user for the partner
                user = User.objects.create_user(
                    username=data['email'], # Use email as username for simplicity
                    email=data['email'],
                    password=data['password']
                )

                # Create an associated ApiClient, which is inactive by default
                api_client = ApiClient.objects.create(
                    user=user,
                    business_name=data['business_name'],
                    website_link=data['website_link']
                )

            # Initiate Paystack payment for the setup fee
            paystack_reference = f"api-setup-{api_client.id}-{uuid.uuid4().hex[:10]}"
            url = "https://api.paystack.co/transaction/initialize"
            headers = {
                "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}",
                "Content-Type": "application/json"
            }
            payload = {
                "email": user.email,
                "amount": str(API_CLIENT_SETUP_FEE * 100),
                "reference": paystack_reference,
                "callback_url": f"{data['website_link']}/api-payment-success",
                "metadata": {
                    "api_client_id": str(api_client.id),
                    "payment_type": "api_setup"
                }
            }

            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()

            if not response_data['status']:
                raise Exception("Failed to initialize Paystack transaction.")

            return Response(response_data['data'], status=status.HTTP_201_CREATED)

        except Exception as e:
            # Clean up created user if payment initiation fails
            if 'user' in locals() and user.id:
                user.delete()
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class APIProjectCreateView(generics.CreateAPIView):
    """
    Allows authenticated API partners to create a new project.
    """
    serializer_class = APIProjectCreateSerializer
    authentication_classes = [APIKeyAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Assigns the owner from the authenticated API client, starts the
        AI pipeline, and increments the usage counter.
        """
        api_client = self.request.user.api_client
        
        # Create the project instance
        project = serializer.save(
            owner=self.request.user,
            name=f"App for {serializer.validated_data['source_url']}" # Auto-generate a name
        )

        # Start the AI agent workflow
        pipeline = chain(
            run_market_analysis.s(project.id),
            run_design_analysis.s(project.id)
        )
        pipeline.delay()

        # Increment the usage counter
        api_client.apps_created_count += 1
        api_client.save()
