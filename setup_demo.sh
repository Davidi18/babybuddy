#!/bin/bash
# סקריפט מהיר להכנת הסביבה והנתונים

echo "🔧 מכין את הסביבה..."
echo ""

# וידוא שמסד הנתונים קיים
if [ ! -f "/tmp/babybuddy_db.sqlite3" ]; then
    echo "📦 יוצר מסד נתונים..."
    python manage.py migrate
    echo ""
fi

# יצירת משתמש אם לא קיים
echo "👤 בודק אם משתמש admin קיים..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'babybuddy.settings.base')
django.setup()
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ משתמש admin נוצר! סיסמה: admin123')
else:
    print('✅ משתמש admin כבר קיים')
"
echo ""

# יצירת נתוני דמה
echo "👶 יוצר נתוני דמה לנועה..."
python manage.py create_bottle_feeding_data --days=7 --name="נועה"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ הכל מוכן!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 פרטי התחברות:"
echo "   👤 שם משתמש: admin"
echo "   🔑 סיסמה: admin123"
echo ""
echo "🚀 להריץ את השרת:"
echo "   ./run_server.sh"
echo "   או: python manage.py runserver 0.0.0.0:8000"
echo ""
