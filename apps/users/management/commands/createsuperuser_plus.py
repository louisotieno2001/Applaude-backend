from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser with a predefined email and password.'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(email='mugash042@gmail.com').exists():
            User.objects.create_superuser('mugash042@gmail.com', '12@Mugash719')
            self.stdout.write(self.style.SUCCESS('Successfully created superuser_plus'))
