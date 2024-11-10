from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import getpass

class Command(BaseCommand):
    help = 'Creates a superuser with predefined email'

    def handle(self, *args, **options):
        email = 'carlosblancosierra@gmail.com'
        username = email

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))
            return

        password = getpass.getpass('Enter password for superuser: ')
        password_confirm = getpass.getpass('Confirm password: ')

        if password != password_confirm:
            self.stdout.write(self.style.ERROR('Passwords do not match'))
            return

        try:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}'))
