#!/usr/bin/env python
"""
סקריפט ליצירת משתמש admin אוטומטית מ-ENV
"""
import os
import django

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
    print(f'ℹ️  משתמש admin כבר קיים: {admin_username}')
