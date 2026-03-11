from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create default admin user for book-service'

    def handle(self, *args, **kwargs):
        username = 'admin'
        password = 'admin14'
        email = 'admin@bookstore.com'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Admin user "{username}" already exists in book-service'))
            return
        
        user = User.objects.create_superuser(username=username, email=email, password=password)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user "{username}" for book-service'))
