#!/usr/bin/env python
"""
סקריפט ליצירת משתמש admin אוטומטית מ-ENV
"""
import os
import sys
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'babybuddy.settings.base')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# קריאת פרטי admin מ-ENV
admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
admin_password = os.environ.get('ADMIN_PASSWORD', 'admin')
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')

# בדיקה אם המשתמש כבר קיים
if not User.objects.filter(username=admin_username).exists():
    User.objects.create_superuser(
        username=admin_username,
        email=admin_email,
        password=admin_password
    )
    print(f'✅ משתמש admin נוצר בהצלחה: {admin_username}')
else:
    # עדכון סיסמה למשתמש קיים
    user = User.objects.get(username=admin_username)
    user.set_password(admin_password)
    user.email = admin_email
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f'🔄 משתמש admin עודכן: {admin_username}')
