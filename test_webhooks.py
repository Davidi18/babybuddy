#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test webhooks and verify the dummy data
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'babybuddy.settings.base')
django.setup()

from core.models import Child, Feeding, Sleep, DiaperChange
from core.analytics import BabyAnalytics

print("=" * 70)
print("🔍 בדיקת הנתונים שנוצרו")
print("=" * 70)

# מציאת הילדה
child = Child.objects.filter(first_name="נועה").first()

if not child:
    print("❌ לא נמצאה תינוקת בשם נועה")
    exit(1)

print(f"\n✅ נמצאה תינוקת: {child.name()}")
print(f"   📅 תאריך לידה: {child.birth_date}")
print(f"   🍼 מצב הנקה: {child.feeding_mode}")

# ספירת רשומות
feeding_count = Feeding.objects.filter(child=child).count()
sleep_count = Sleep.objects.filter(child=child).count()
diaper_count = DiaperChange.objects.filter(child=child).count()

print(f"\n📊 סטטיסטיקות:")
print(f"   🍼 האכלות: {feeding_count}")
print(f"   💤 שינה: {sleep_count}")
print(f"   🧷 חיתולים: {diaper_count}")

# בדיקה שכל ההאכלות הן בבקבוק
bottle_feedings = Feeding.objects.filter(child=child, method='bottle').count()
print(f"\n🍼 האכלות בבקבוק: {bottle_feedings}/{feeding_count}")

if bottle_feedings == feeding_count:
    print("   ✅ כל ההאכלות הן בבקבוק!")
else:
    print(f"   ⚠️  יש {feeding_count - bottle_feedings} האכלות שאינן בבקבוק")

# הצגת כמה דוגמאות
print("\n🔍 דוגמאות האכלות אחרונות:")
for feeding in Feeding.objects.filter(child=child).order_by('-start')[:5]:
    print(f"   📅 {feeding.start.strftime('%Y-%m-%d %H:%M')} - "
          f"{feeding.method} - {feeding.type} - {feeding.amount}ml")

print("\n" + "=" * 70)
print("🔍 בדיקת Analytics והוובהוקים")
print("=" * 70)

analytics = BabyAnalytics(child)

# סיכום יומי
print("\n📊 סיכום יומי:")
daily_summary = analytics.get_daily_summary()
print(json.dumps(daily_summary, indent=2, ensure_ascii=False))

# מצב נוכחי
print("\n📊 מצב נוכחי:")
status = analytics.get_current_status()

if status.get('last_feeding'):
    last_feeding = status['last_feeding']
    print(f"   🍼 האכלה אחרונה: לפני {last_feeding['time_since_formatted']}")
    print(f"      כמות: {last_feeding.get('amount', 'N/A')}ml")

if status.get('last_sleep'):
    last_sleep = status['last_sleep']
    print(f"   💤 שינה אחרונה: ער {last_sleep['time_since_formatted']}")

if status.get('last_diaper'):
    last_diaper = status['last_diaper']
    print(f"   🧷 חיתול אחרון: לפני {last_diaper['time_since_formatted']}")

# חיזויים
print("\n🔮 חיזויים:")
next_feeding = analytics.predict_next_feeding()
if next_feeding:
    print(f"   🍼 האכלה הבאה: {next_feeding['message']}")
    print(f"      סטטוס: {next_feeding['status']}")

next_sleep = analytics.predict_next_sleep()
if next_sleep:
    print(f"   💤 שינה הבאה: {next_sleep['message']}")
    print(f"      סטטוס: {next_sleep['status']}")

print("\n" + "=" * 70)
print("✅ הבדיקה הושלמה בהצלחה!")
print("=" * 70)

print("\n📝 הוראות שימוש:")
print("   1. הפעל את השרת: python manage.py runserver")
print("   2. גש לדף הבית: http://localhost:8000/")
print(f"   3. גש לדף של נועה: http://localhost:8000/children/{child.slug}/")
print("   4. בדוק webhooks:")
print(f"      - /api/webhooks/daily-summary/?child={child.slug}")
print(f"      - /api/webhooks/status/?child={child.slug}")
print(f"      - /api/webhooks/alerts/?child={child.slug}")
print("\n   💡 כדי לבדוק webhooks עם authentication, צור משתמש:")
print("      python manage.py createsuperuser")
