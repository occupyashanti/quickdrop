import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickdrop.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction

def create_superuser():
    if not User.objects.filter(username='admin').exists():
        with transaction.atomic():
            superuser = User.objects.create_superuser(
                username='admin',
                email='admin@quickdrop.com',
                password='adminpass123'
            )
            print(f"Superuser created: {superuser.username}")
    else:
        print("Superuser 'admin' already exists")
