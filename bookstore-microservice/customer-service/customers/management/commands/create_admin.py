from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from customers.models import UserProfile


class Command(BaseCommand):
    help = 'Create default admin user if not exists'

    def handle(self, *args, **kwargs):
        username = 'admin'
        password = 'admin14'
        email = 'admin@bookstore.com'
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Admin user "{username}" already exists'))
            return
        
        # Create admin user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        # Create admin profile with manager role
        UserProfile.objects.create(
            user=user,
            role=UserProfile.ROLE_MANAGER,
            customer=None  # Admin is not a customer
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user "{username}" with password "{password}"'))
