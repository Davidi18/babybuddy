# 🔗 Baby Buddy Webhooks למערכות אוטומציה
# Webhooks for n8n, Zapier, Make.com & More

מדריך לשילוב Baby Buddy עם מערכות אוטומציה כמו n8n, Zapier, Make.com ועוד.

---

## 🎯 סקירה כללית

הוספנו 3 webhook endpoints שמאפשרים לך:
- ✅ לקבל סיכום יומי כל בוקר (WhatsApp / Telegram / Email)
- ✅ לבדוק מצב נוכחי כל X דקות
- ✅ לקבל התראות רק כשיש משהו דחוף

---

## 📍 Webhook Endpoints

### Base URL
```
https://your-baby-buddy-domain.com/api/webhooks/
```

### Authentication
כל ה-webhooks דורשים **API Token**.

ליצירת token:
```bash
python manage.py drf_create_token your_username
```

---

## 1️⃣ Daily Summary Webhook

**שליחת סיכום יומי כל בוקר** - מתאים לשליחה בהודעה.

### Endpoint
```
GET/POST /api/webhooks/daily-summary/
```

### Parameters
- `child` (optional) - slug של הילד. אם לא מסופק, לוקח את הילד הראשון.

### Example Request

**cURL:**
```bash
curl -X GET \
  "https://baby.example.com/api/webhooks/daily-summary/?child=emma" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**n8n HTTP Request Node:**
```
URL: https://baby.example.com/api/webhooks/daily-summary/
Method: GET
Authentication: Generic Credential Type
  Header Auth:
    Name: Authorization
    Value: Token YOUR_API_TOKEN
Query Parameters:
  child: emma
```

### Response Example

```json
{
  "success": true,
  "timestamp": "2025-01-15T08:00:00Z",
  "child": {
    "name": "Emma Smith",
    "slug": "emma"
  },
  "message": "📊 סיכום יומי - Emma Smith\n📅 15/01/2025\n\n🍼 האכלות היום:\n  • 8 האכלות\n  • 185 דקות\n  • 950 ml\n\n💤 שינה היום:\n  • 5 תקופות שינה\n  • 12.5 שעות\n  • 3 תנומות\n\n🧷 חיתולים היום:\n  • 9 חיתולים\n\n📈 ממוצעים שבועיים:\n  • האכלה כל 180 דקות\n  • 13.2 שעות שינה ביום\n\n🔮 חיזויים:\n  • האכלה הבאה: בעוד ~2 שעות\n  • שינה: בעוד ~30 דקות",
  "data": {
    "today": {
      "date": "2025-01-15",
      "feedings": {
        "count": 8,
        "total_duration_minutes": 185.5,
        "total_amount": 950.0
      },
      "sleep": {
        "count": 5,
        "total_duration_minutes": 750.0,
        "total_duration_hours": 12.5,
        "naps": 3
      },
      "diapers": {
        "count": 9,
        "wet": 7,
        "solid": 4
      }
    },
    "stats_7_days": { ... },
    "predictions": { ... }
  },
  "alerts": [
    {
      "type": "feeding_overdue",
      "severity": "high",
      "message": "עבר הזמן! התינוק כנראה רעב"
    }
  ]
}
```

### השדה `message`
טקסט מעוצב מוכן לשליחה! פשוט העתק אותו להודעה.

---

## 2️⃣ Status Webhook

**בדיקת מצב נוכחי** - מתאים לבדיקות תכופות (כל 5-15 דקות).

### Endpoint
```
GET/POST /api/webhooks/status/
```

### Parameters
- `child` (optional)

### Example Request

```bash
curl -X GET \
  "https://baby.example.com/api/webhooks/status/?child=emma" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Response Example

```json
{
  "success": true,
  "timestamp": "2025-01-15T14:30:00Z",
  "child": {
    "name": "Emma Smith",
    "slug": "emma"
  },
  "status_text": "👶 Emma Smith | 🍼 האכלה: לפני 2:15 | 💤 ער: 1:30 | ⚠️ בקרוב! בעוד ~15 דקות",
  "last_feeding_minutes_ago": 135.0,
  "last_sleep_minutes_ago": 90.0,
  "last_diaper_minutes_ago": 105.0,
  "next_feeding_status": "soon",
  "next_sleep_status": "awake",
  "alerts": []
}
```

---

## 3️⃣ Alerts Webhook

**התראות בלבד** - מחזיר תוצאה רק אם יש משהו דחוף!

### Endpoint
```
GET/POST /api/webhooks/alerts/
```

### Example Request

```bash
curl -X GET \
  "https://baby.example.com/api/webhooks/alerts/?child=emma" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Response - אין התראות

```json
{
  "success": true,
  "has_alerts": false,
  "message": "הכל בסדר! אין התראות",
  "child": {
    "name": "Emma Smith",
    "slug": "emma"
  }
}
```

### Response - יש התראות!

```json
{
  "success": true,
  "has_alerts": true,
  "alert_count": 2,
  "child": {
    "name": "Emma Smith",
    "slug": "emma"
  },
  "alerts": [
    {
      "type": "feeding_overdue",
      "severity": "high",
      "title": "התינוק רעב!",
      "message": "עבר הזמן! התינוק כנראה רעב (איחור של 25 דקות)",
      "minutes_overdue": 25.0
    },
    {
      "type": "diaper_overdue",
      "severity": "medium",
      "title": "זמן לחיתול",
      "message": "עברו 3.5 שעות מחיתול אחרון",
      "hours_since": 3.5
    }
  ],
  "timestamp": "2025-01-15T14:30:00Z"
}
```

---

## 🤖 n8n - דוגמאות Workflows

### 📱 Workflow 1: סיכום יומי בוואטסאפ (כל בוקר ב-8)

**Nodes:**

1. **Schedule Trigger** (כל יום ב-8:00)
   - Mode: Every day
   - Hour: 8
   - Minute: 0

2. **HTTP Request** - קרא ל-webhook
   - Method: GET
   - URL: `https://baby.example.com/api/webhooks/daily-summary/?child=emma`
   - Authentication: Header Auth
     - Name: `Authorization`
     - Value: `Token YOUR_API_TOKEN`

3. **Set** - הכן את ההודעה
   - Keep Only Set: true
   - Values:
     - `message` = `{{ $json.message }}`
     - `has_alerts` = `{{ $json.alerts.length > 0 }}`

4. **WhatsApp** (או Telegram) - שלח הודעה
   - To: מספר הטלפון שלך
   - Message: `{{ $json.message }}`

**זהו! כל בוקר ב-8 תקבל סיכום של אתמול + תחזית להיום.**

---

### ⏰ Workflow 2: התראות כל 15 דקות (אם התינוק רעב/עייף)

**Nodes:**

1. **Schedule Trigger**
   - Mode: Every 15 minutes

2. **HTTP Request** - בדוק התראות
   - Method: GET
   - URL: `https://baby.example.com/api/webhooks/alerts/?child=emma`
   - Authentication: Header Auth

3. **IF** - יש התראות?
   - Condition: `{{ $json.has_alerts }}` equals `true`

4. **Switch** (מהענף True של IF) - לפי סוג התראה
   - Mode: Rules
   - Rules:
     - Rule 1: `{{ $json.alerts[0].type }}` equals `feeding_overdue` → Output 0
     - Rule 2: `{{ $json.alerts[0].type }}` equals `overtired` → Output 1
     - Default → Output 2

5. **WhatsApp / Telegram** (3 nodes, אחד לכל output)
   - Output 0 (רעב): הודעה "🍼 התינוק רעב!"
   - Output 1 (עייף): הודעה "😴 התינוק עייף!"
   - Output 2 (אחר): הודעה כללית

**תקבל התראה רק כשיש משהו דחוף!**

---

### 📊 Workflow 3: מצב נוכחי כל שעה

**Nodes:**

1. **Schedule Trigger**
   - Mode: Every hour

2. **HTTP Request**
   - URL: `https://baby.example.com/api/webhooks/status/?child=emma`

3. **Set** - עצב את ההודעה
   - `status_message` = `{{ $json.status_text }}`

4. **Telegram / Slack** - שלח עדכון
   - Message: `{{ $json.status_message }}`

---

### 🏠 Workflow 4: שילוב עם Home Assistant

**Nodes:**

1. **Schedule Trigger** - כל 10 דקות

2. **HTTP Request** - קבל מצב
   - URL: `https://baby.example.com/api/webhooks/status/?child=emma`

3. **Home Assistant** - עדכן sensors
   - Entity: `sensor.baby_last_feeding`
   - State: `{{ $json.last_feeding_minutes_ago }}`

4. **Home Assistant** - עדכן alert
   - Entity: `binary_sensor.baby_needs_feeding`
   - State: `{{ $json.next_feeding_status === "overdue" ? "on" : "off" }}`

---

## 🔐 אבטחה

### 1. שמור על ה-Token בסוד!
```bash
# ב-n8n, שמור ב-Credentials
# אל תשתף את ה-token בפומבי
```

### 2. HTTPS חובה!
```bash
# וודא ש-Coolify מגדיר HTTPS
SECURE_SSL_REDIRECT=True
```

### 3. הגבל גישה
אפשר להגביל גישה ל-IP ספציפי ב-Coolify.

---

## 🧪 בדיקות

### בדוק עם cURL

```bash
# בדוק שה-webhook עובד
curl -X GET \
  "http://localhost:8000/api/webhooks/status/" \
  -H "Authorization: Token YOUR_TOKEN"

# אם עובד - תקבל JSON עם נתונים
```

### בדוק ב-n8n

1. צור **HTTP Request node**
2. הגדר את ה-URL וה-Token
3. לחץ **Execute Node**
4. אמור לראות את התוצאה!

---

## 💡 רעיונות נוספים

### 📲 שליחת קישורים
```json
{
  "message": "🍼 זמן האכלה!\n\nהקלק כאן להוספה:\nhttps://baby.example.com/feedings/add/"
}
```

### 📊 שמירה ב-Google Sheets
n8n → HTTP Request → Google Sheets (append row)

### 🔔 התראות מותאמות
```javascript
// ב-n8n Function node
if ($json.last_feeding_minutes_ago > 240) {
  return {
    alert: true,
    message: "⚠️ עברו יותר מ-4 שעות מהאכלה!"
  };
}
```

### 🏡 אוטומציה של הבית
- הדלק אור כשהתינוק ער יותר מ-90 דקות
- שנה צבע נורה כשהגיע זמן האכלה
- הפעל מוזיקה כשהתינוק עייף

---

## 📋 Checklist להתקנה

- [ ] יצרת API Token: `python manage.py drf_create_token username`
- [ ] בדקת ש-webhook עובד עם cURL
- [ ] יצרת workflow ב-n8n
- [ ] הוספת את ה-Token ל-n8n Credentials
- [ ] הגדרת שעות (למשל 8:00 לסיכום יומי)
- [ ] בדקת שההודעות מגיעות
- [ ] 🎉 נהנה מאוטומציה!

---

## 🐛 פתרון בעיות

### שגיאה: "Authentication credentials were not provided"
➡️ שכחת להוסיף את ה-Token ב-Header

**תיקון:**
```
Authorization: Token YOUR_API_TOKEN
```

### שגיאה: "Child not found"
➡️ ה-slug לא נכון

**תיקון:**
```bash
# בדוק מה ה-slug
curl http://localhost:8000/api/children/ -H "Authorization: Token TOKEN"
```

### שגיאה: 404
➡️ ה-URL לא נכון

**תיקון:**
```
https://YOUR_DOMAIN/api/webhooks/daily-summary/
                   ^^^^ אל תשכח את api/
```

---

## 🆘 עזרה

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community](https://community.n8n.io/)
- [Baby Buddy GitHub](https://github.com/babybuddy/babybuddy)

---

**🎉 בהצלחה! לקראת הלידה של התינוקת! 👶💕**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
