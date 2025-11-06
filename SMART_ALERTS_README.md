# 🎯 Smart Alerts System - Update November 2025

## מה חדש?

הוספנו מערכת התראות **חכמה** ל-Baby Buddy webhooks עם:

### ✨ תכונות:

1. **🎛️ Thresholds מותאמים** - שליטה על מתי להתריע
2. **🌙 שעות שקטות** - לא מפריעים בלילה (22:00-07:00)
3. **⏸️ Snooze** - לא שולחים אותה התראה פעמיים ב-30 דקות
4. **📊 שקיפות** - כל התראה מציגה את הסף ששימש

---

## 📦 הקבצים:

- **`api/smart_webhook_additions.py`** - הפונקציה החדשה
- **`SMART_ALERTS_GUIDE.md`** - מדריך מפורט
- **`N8N_SMART_ALERTS_WORKFLOW.md`** - הוראות ליצירת workflow

---

## 🚀 איך להתקין?

### שלב 1: הוסף את הפונקציה
```python
# העתק את התוכן של api/smart_webhook_additions.py
# והדבק אותו בסוף api/webhook_views.py
```

### שלב 2: הוסף URL
הוסף ל-`api/urls.py` את השורה:
```python
path(
    "api/webhooks/smart-alerts/",
    webhook_views.smart_alerts_webhook,
    name="webhook-smart-alerts",
),
```

### שלב 3: Restart Baby Buddy

### שלב 4: בדוק שזה עובד
```bash
curl "https://baby.example.com/api/webhooks/smart-alerts/?child=emma" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## 💡 שימוש ב-n8n:

**URL חדש:**
```
/api/webhooks/smart-alerts/?child=emma&feeding_threshold=20&quiet_hours_start=23
```

**פרמטרים:**
- `feeding_threshold=20` - התראה אחרי 20 דקות איחור
- `sleep_threshold=100` - התראה אחרי 100 דקות ער
- `quiet_hours_start=22` - התחל שקט ב-22:00
- `quiet_hours_end=7` - סיים שקט ב-07:00
- `snooze_minutes=30` - המתן 30 דקות בין התראות

---

## 📚 תיעוד מלא:

ראה `SMART_ALERTS_GUIDE.md` למדריך מפורט.

---

**בהצלחה! לקראת הלידה של התינוקת!** 👶💕🍼
