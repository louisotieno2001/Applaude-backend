import os
import requests
import hmac
import hashlib
import json
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.projects.models import Project
from .models import Payment
from agents.tasks import run_code_generation, run_qa_check, run_deployment
from celery import chain

# Base prices in USD
BASE_PLAN_PRICES_USD = {
    'ONETIME': Decimal('50.00'),
    'MONTHLY': Decimal('15.00'),
    'YEARLY': Decimal('150.00'),
}

# Mock conversion rates for demonstration
COUNTRY_CURRENCY_CONVERSION = {
    'NG': {'currency': 'NGN', 'rate': Decimal('1400')}, # Nigeria
    'KE': {'currency': 'KES', 'rate': Decimal('130')},  # Kenya
    'GH': {'currency': 'GHS', 'rate': Decimal('15')},   # Ghana
    'FR': {'currency': 'EUR', 'rate': Decimal('0.92')},  # France
    'DE': {'currency': 'EUR', 'rate': Decimal('0.92')},  # Germany
    'JP': {'currency': 'JPY', 'rate': Decimal('155')},  # Japan
    'IN': {'currency': 'INR', 'rate': Decimal('83')},   # India
    'CN': {'currency': 'CNY', 'rate': Decimal('7.2')},   # China
    'RU': {'currency': 'RUB', 'rate': Decimal('90')},    # Russia
    'BR': {'currency': 'BRL', 'rate': Decimal('5.1')},   # Brazil
    'GB': {'currency': 'GBP', 'rate': Decimal('0.8')},   # UK
}

class GetLocalizedPricingView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        country_code = request.query_params.get('country', 'US').upper()

        if country_code in COUNTRY_CURRENCY_CONVERSION:
            conversion = COUNTRY_CURRENCY_CONVERSION[country_code]
            currency = conversion['currency']
            rate = conversion['rate']
            localized_prices = {plan: (price * rate).quantize(Decimal('0.01')) for plan, price in BASE_PLAN_PRICES_USD.items()}
        else:
            currency = 'USD'
            localized_prices = BASE_PLAN_PRICES_USD

        return Response({
            'currency': currency,
            'prices': localized_prices
        })


class InitializePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        project_id = request.data.get('project_id')
        plan_type = request.data.get('plan_type')
        currency = request.data.get('currency', 'USD').upper()

        if not all([project_id, plan_type]):
            return Response({'error': 'Project ID and Plan Type are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if plan_type not in BASE_PLAN_PRICES_USD:
            return Response({'error': 'Invalid plan type.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.select_related('owner').get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

        if currency != 'USD' and currency in [c['currency'] for c in COUNTRY_CURRENCY_CONVERSION.values()]:
            country_code = next((code for code, data in COUNTRY_CURRENCY_CONVERSION.items() if data['currency'] == currency), None)
            if country_code:
                rate = COUNTRY_CURRENCY_CONVERSION[country_code]['rate']
                amount = (BASE_PLAN_PRICES_USD[plan_type] * rate).quantize(Decimal('0.01'))
            else:
                amount = BASE_PLAN_PRICES_USD[plan_type]
                currency = 'USD'
        else:
            amount = BASE_PLAN_PRICES_USD[plan_type]
            currency = 'USD'

        email = request.user.email
        paystack_reference = f"applause-{project_id}-{uuid.uuid4().hex[:12]}"

        Payment.objects.create(
            user=request.user, project=project, amount=amount,
            email=email, plan_type=plan_type, paystack_reference=paystack_reference
        )

        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {os.getenv('PAYSTACK_SECRET_KEY')}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": str(int(amount * 100)),
            "reference": paystack_reference,
            "currency": currency,
            "callback_url": f"http://localhost:5173/project/{project.id}?payment=success"
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()
            if response_data['status']:
                return Response(response_data['data'])
            else:
                return Response({'error': f"Failed to initialize payment: {response_data.get('message')}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
