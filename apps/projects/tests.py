from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()

class ProjectAPITests(APITestCase):

    def setUp(self):
        # Create a user and token for authentication
        self.user = User.objects.create_user(email='test@applaude.ai', password='password123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # URLs
        self.create_url = reverse('project-create')
        self.list_url = reverse('project-list')

        # Project Data
        self.project_data = {
            'name': 'Test Project',
            'website_url': 'https://example.com',
            'app_type': 'iOS'
        }

    def test_create_project_authenticated(self):
        """
        Ensure an authenticated user can create a new project.
        """
        response = self.client.post(self.create_url, self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, 'Test Project')

    def test_create_project_unauthenticated(self):
        """
        Ensure an unauthenticated user cannot create a project.
        """
        self.client.logout()
        response = self.client.post(self.create_url, self.project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_projects(self):
        """
        Ensure an authenticated user can list their own projects.
        """
        # Create a project for the user
        Project.objects.create(user=self.user, **self.project_data)

        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.project_data['name'])

    def test_list_projects_isolates_data(self):
        """
        Ensure a user cannot see projects created by another user.
        """
        # Create a project for the main test user
        Project.objects.create(user=self.user, **self.project_data)

        # Create another user and their project
        other_user = User.objects.create_user(email='other@applaude.ai', password='password123')
        Project.objects.create(user=other_user, name='Other Project', website_url='https://other.com', app_type='Android')

        # The main user should only see their own project
        response = self.client.get(self.list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertNotEqual(response.data[0]['name'], 'Other Project')
