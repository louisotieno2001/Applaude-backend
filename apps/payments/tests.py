from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.projects.models import Project
from .models import Payment

User = get_user_model()

class PaymentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword123'
        )
        self.project = Project.objects.create(
            owner=self.user,
            name='Test Project',
            source_url='http://example.com',
            app_type=Project.AppType.ANDROID
        )

    def test_create_payment(self):
        """Test creating a payment object."""
        payment = Payment.objects.create(
            user=self.user,
            project=self.project,
            amount=50.00,
            email=self.user.email,
            plan_type=Payment.PlanType.ONETIME
        )
        self.assertEqual(payment.amount, 50.00)
        self.assertEqual(payment.status, Payment.PaymentStatus.PENDING)
        self.assertEqual(str(payment), f"Payment of {payment.amount} for {self.project.name} ({payment.plan_type} - {payment.status})")
