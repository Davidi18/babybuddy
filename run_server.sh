#!/bin/bash
# Script to run Baby Buddy development server

echo "🚀 מריץ את שרת Baby Buddy..."
echo ""
echo "📝 פרטי התחברות:"
echo "   👤 שם משתמש: admin"
echo "   🔑 סיסמה: בדוק בקובץ .env או השתמש בסיסמה שהגדרת"
echo ""
echo "🔗 כתובות חשובות:"
echo "   🏠 דף הבית: http://localhost:8000/"
echo "   👶 דף נועה: http://localhost:8000/children/נועה/"
echo "   📊 Dashboard: http://localhost:8000/dashboard/"
echo ""
echo "🔗 Webhooks לבדיקה:"
echo "   📊 /api/webhooks/daily-summary/?child=נועה"
echo "   🔄 /api/webhooks/status/?child=נועה"
echo "   ⚠️  /api/webhooks/alerts/?child=נועה"
echo ""
echo "▶️  השרת רץ..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python manage.py runserver 0.0.0.0:8000
