# 🎯 Smart Alerts System - מערכת התראות חכמה

## מה חדש?

הוספנו endpoint חדש: `/api/webhooks/smart-alerts/` עם יכולות מתקדמות:

### ✨ תכונות חדשות:

1. **🎛️ Thresholds מותאמים אישית** - שליטה מלאה על מתי מתריעים
2. **🌙 שעות שקטות** - לא להפריע בלילה
3. **⏸️ Snooze חכם** - לא לשלוח אותה התראה פעמיים
4. **📊 שקיפות מלאה** - תמיד יודעים איזה threshold שימש

---

## 📖 איך להשתמש?

### בסיסי - כמו קודם:
```bash
GET /api/webhooks/smart-alerts/?child=emma
```

### מתקדם - עם התאמה אישית:
```bash
# התראת האכלה רק אחרי 20 דקות איחור (במקום 15)
GET /api/webhooks/smart-alerts/?feeding_threshold=20

# התראת עייפות רק אחרי 100 דקות ער (במקום 90)
GET /api/webhooks/smart-alerts/?sleep_threshold=100

# חיתול רק אחרי 4 שעות (במקום 3)
GET /api/webhooks/smart-alerts/?diaper_threshold=240

# שעות שקטות: 23:00-06:00 (במקום 22:00-07:00)
GET /api/webhooks/smart-alerts/?quiet_hours_start=23&quiet_hours_end=6

# Snooze של 45 דקות (במקום 30)
GET /api/webhooks/smart-alerts/?snooze_minutes=45

# כל הפרמטרים ביחד:
GET /api/webhooks/smart-alerts/?child=emma&feeding_threshold=20&sleep_threshold=100&quiet_hours_start=23&quiet_hours_end=6&snooze_minutes=45
```

---

## 🌙 שעות שקטות

**ברירת מחדל:** 22:00-07:00 (לא שולחים התראות)

**דוגמה לתשובה בשעות שקטות:**
```json
{
  "success": true,
  "has_alerts": false,
  "message": "🌙 שעות שקטות (22:00-7:00) - לא שולחים התראות",
  "quiet_hours": true,
  "current_hour": 23
}
```

**כיצד לכבות את שעות השקטות:**
```bash
GET /api/webhooks/smart-alerts/?respect_quiet_hours=false
```

---

## ⏸️ Snooze - איך זה עובד?

נניח ששלחת התראה "התינוקת רעבה!" ב-10:00.

עם snooze של 30 דקות:
- ⏰ 10:00 - שולחים התראה
- 🔇 10:15 - n8n בודק, אבל לא שולח (snooze פעיל)
- 🔇 10:30 - n8n בודק, עדיין snooze
- ⏰ 10:45 - snooze נגמר, אם עדיין רעבה - שולחים שוב!

**למה זה חשוב?**
- מונע spam של התראות
- נותן לך זמן להגיב
- אבל לא שוכח אם עדיין לא טיפלת

---

## 📊 דוגמה לתשובה עם התראה:

```json
{
  "success": true,
  "has_alerts": true,
  "alert_count": 1,
  "alerts": [
    {
      "type": "feeding_overdue",
      "severity": "high",
      "title": "Emma רעבה!",
      "message": "עבר זמן האכלה! איחור של 22 דקות",
      "minutes_overdue": 22,
      "threshold_used": 15
    }
  ],
  "quiet_hours": false,
  "thresholds": {
    "feeding": 15,
    "sleep": 90,
    "diaper": 180
  },
  "snooze_minutes": 30
}
```

---

## 💡 טיפים לשימוש:

### 1. התאמה לפי גיל התינוקת
```bash
# תינוקת חדשה (1-2 חודשים) - סבלנות יותר
?feeding_threshold=10&sleep_threshold=60

# תינוקת יותר גדולה (3-6 חודשים) - פחות סבלנות
?feeding_threshold=20&sleep_threshold=120
```

### 2. סופ"ש vs ימי חול
ב-n8n תוכל לעשות IF:
```javascript
// אם זה שבת
if (new Date().getDay() === 6) {
  url = "?feeding_threshold=30"  // יותר סבלנות
} else {
  url = "?feeding_threshold=15"  // ימי חול רגיל
}
```

---

## 🚀 התקנה

### שלב 1: הוסף את הפונקציה
העתק את הקוד מ-`api/smart_webhook_additions.py` לסוף `api/webhook_views.py`

### שלב 2: הוסף את ה-URL
הוסף ל-`api/urls.py`:
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
curl -X GET \
  "https://baby.example.com/api/webhooks/smart-alerts/?child=emma" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## 🎉 בהצלחה!

עכשיו יש לך מערכת התראות **חכמה** ו**גמישה**! 🍼👶💕
