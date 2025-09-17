from django.core.management.base import BaseCommand
from Dashboard.models import AdminUser
from django.conf import settings
from decouple import config

class Command(BaseCommand):
    help = 'Create a superuser if none exists'

    def handle(self, *args, **kwargs):
        if not AdminUser.objects.filter(is_superuser=True).exists():
            username = config('SUPERUSER_NAME', default='admin')
            password = config('SUPERUSER_PASSWORD', default='admin123')
            email = config('SUPERUSER_EMAIL', default="admin@gmail.com")
            AdminUser.objects.create_superuser(username=username, password=password, email=email)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully.'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists. No action taken.'))