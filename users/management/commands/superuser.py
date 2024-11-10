from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser with predefined email'

    def handle(self, *args, **options):
        email = 'carlosblancosierra@gmail.com'

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superuser with email "{email}" already exists'))
            return

        password = getpass.getpass('Enter password for superuser: ')
        password_confirm = getpass.getpass('Confirm password: ')

        if password != password_confirm:
            self.stdout.write(self.style.ERROR('Passwords do not match'))
            return

        try:
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser with email "{email}" created successfully'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating superuser: {str(e)}'))
