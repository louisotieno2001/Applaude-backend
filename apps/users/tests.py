from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthTests(APITestCase):

    def test_user_registration(self):
        """
        Ensure we can register a new user.
        """
        url = reverse('register')
        data = {'email': 'testuser@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().email, 'testuser@example.com')

    def test_user_login(self):
        """
        Ensure a registered user can log in and get a token.
        """
        # First, create the user
        User.objects.create_user(email='login@example.com', password='password123')

        # Then, attempt to log in
        url = reverse('token_obtain_pair')
        data = {'email': 'login@example.com', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
