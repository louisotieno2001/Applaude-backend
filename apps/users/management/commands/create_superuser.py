from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser if it does not exist'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Superuser email')
        parser.add_argument('--password', type=str, help='Superuser password')

    def handle(self, *args, **options):
        email = options.get('email') or getattr(settings, 'DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = options.get('password') or getattr(settings, 'DJANGO_SUPERUSER_PASSWORD', 'admin123')

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superuser with email {email} already exists'))
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            first_name='Admin',
            last_name='User'
        )

        self.stdout.write(self.style.SUCCESS(f'Superuser created successfully with email: {email}'))
