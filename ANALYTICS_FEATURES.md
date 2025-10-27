# 📊 Baby Buddy Analytics & Predictions

# אנליטיקה וחיזויים ל-Baby Buddy

תכונות אנליטיקה מתקדמות ופקודות ניהול שימושיות עבור Baby Buddy.

---

## 🎯 תוכן עניינים / Table of Contents

1. [סקירה כללית](#סקירה-כללית)
2. [Analytics Module - מודול האנליטיקה](#analytics-module)
3. [Management Commands - פקודות ניהול](#management-commands)
4. [API Endpoints - נקודות קצה](#api-endpoints)
5. [דוגמאות שימוש](#דוגמאות-שימוש)
6. [התקנה ושימוש](#התקנה-ושימוש)

---

## סקירה כללית / Overview

### מה נוסף?

תוסף זה מוסיף ל-Baby Buddy:

- **🧮 לוגיקת חיזוי חכמה** - מנבא מתי התינוק יהיה רעב/עייף
- **📊 סטטיסטיקות מתקדמות** - ממוצעים, דפוסים וניתוחים
- **⚙️ פקודות ניהול** - גיבויים אוטומטיים, סיכומים יומיים ועוד
- **🔌 API מורחב** - endpoints חדשים לאנליטיקה

### למה זה שימושי?

- ✅ **למד את דפוסי התינוק** - מתי הוא אוכל, ישן ויותר
- ✅ **חזה אירועים** - דע מתי התינוק יהיה רעב או עייף
- ✅ **סיכומים אוטומטיים** - קבל דוח יומי מפורט
- ✅ **גיבויים קלים** - גבה את הנתונים שלך בקלות
- ✅ **API למפתחים** - בנה אפליקציות משלך מעל הנתונים

---

## Analytics Module

### 📁 קובץ: `core/analytics.py`

מודול מרכזי עם מחלקה `BabyAnalytics` שמספקת כל הלוגיקה של חיזוי וסטטיסטיקות.

### אתחול

```python
from core.models import Child
from core.analytics import BabyAnalytics

child = Child.objects.first()
analytics = BabyAnalytics(child)
```

---

### 🍼 Feeding Analytics - אנליטיקת האכלות

#### `get_feeding_stats(days=7)`

מחזיר סטטיסטיקות על האכלות בימים האחרונים.

**פרמטרים:**

- `days` (int): מספר ימים לניתוח (ברירת מחדל: 7)

**מחזיר:**

```python
{
    "count": 42,  # מספר האכלות
    "average_duration_minutes": 25.5,  # משך ממוצע
    "average_interval_minutes": 180.0,  # מרווח ממוצע בין האכלות
    "total_amount": 850.0,  # כמות כוללת (אם נרשמה)
    "by_type": {
        "breast milk": 30,
        "formula": 12
    },
    "period_days": 7
}
```

**דוגמה:**

```python
stats = analytics.get_feeding_stats(days=7)
print(f"ממוצע בין האכלות: {stats['average_interval_minutes']} דקות")
```

---

#### `get_last_feeding_info()`

מחזיר מידע על האכלה אחרונה וכמה זמן עבר מאז.

**מחזיר:**

```python
{
    "feeding": Feeding object,
    "time_since_minutes": 120.5,
    "time_since_hours": 2.0,
    "time_since_formatted": "2:00",
    "type": "breast milk",
    "amount": 150.0
}
```

---

#### `predict_next_feeding()`

🔮 **מנבא מתי תהיה ההאכלה הבאה** בהתבסס על דפוסים היסטוריים.

**לוגיקת החיזוי:**

1. מחשב ממוצע מרווח בין האכלות (7 ימים אחרונים)
2. בודק כמה זמן עבר מהאכלה אחרונה
3. מחשב מתי צפויה האכלה הבאה

**מחזיר:**

```python
{
    "status": "soon",  # או: "overdue", "upcoming", "later"
    "message": "בקרוב! בעוד ~30 דקות",
    "minutes_until_next": 30.0,
    "estimated_time": datetime object,
    "average_interval_minutes": 180.0,
    "confidence": "high"  # או: "medium"
}
```

**סטטוסים:**

- `overdue` - עבר הזמן, התינוק כנראה רעב!
- `soon` - בעוד פחות מ-30 דקות
- `upcoming` - בעוד 30-60 דקות
- `later` - בעוד יותר משעה

**דוגמה:**

```python
prediction = analytics.predict_next_feeding()
if prediction:
    print(f"סטטוס: {prediction['status']}")
    print(f"הודעה: {prediction['message']}")
    print(f"זמן משוער: {prediction['estimated_time'].strftime('%H:%M')}")
```

---

### 💤 Sleep Analytics - אנליטיקת שינה

#### `get_sleep_stats(days=7)`

מחזיר סטטיסטיקות על שינה בימים האחרונים.

**מחזיר:**

```python
{
    "count": 35,
    "total_sleep_hours": 98.5,
    "average_sleep_hours_per_day": 14.1,
    "naps_count": 21,
    "night_sleep_count": 14,
    "average_nap_duration_minutes": 45.0,
    "period_days": 7
}
```

---

#### `get_last_sleep_info()`

מידע על שינה אחרונה.

**מחזיר:**

```python
{
    "sleep": Sleep object,
    "time_since_minutes": 90.0,
    "time_since_hours": 1.5,
    "time_since_formatted": "1:30",
    "was_nap": True,
    "duration_minutes": 45.0
}
```

---

#### `predict_next_sleep()`

🔮 **מנבא מתי התינוק יתעייף** בהתבסס על "חלון ערות" טיפוסי.

**לוגיקת החיזוי:**

- משתמש ב-"wake window" - זמן טיפוסי שתינוק יכול להיות ער
- ברירת מחדל: 90 דקות (ניתן לשיפור לפי גיל)
- מחשב כמה זמן עבר מאז השינה האחרונה

**מחזיר:**

```python
{
    "status": "awake",  # או: "overtired", "getting_tired", "soon"
    "message": "עוד 30 דקות עד שיתעייף",
    "minutes_awake": 60.0,
    "minutes_until_tired": 30.0,
    "typical_wake_window_minutes": 90
}
```

---

### 🧷 Diaper Analytics - אנליטיקת חיתולים

#### `get_diaper_stats(days=7)`

```python
{
    "count": 56,
    "wet_count": 45,
    "solid_count": 28,
    "average_per_day": 8.0,
    "period_days": 7
}
```

#### `get_last_diaper_info()`

```python
{
    "change": DiaperChange object,
    "time_since_minutes": 120.0,
    "time_since_hours": 2.0,
    "time_since_formatted": "2:00",
    "was_wet": True,
    "was_solid": False
}
```

---

### 📅 סיכומים משולבים

#### `get_daily_summary(date=None)`

סיכום מלא של כל הפעילויות ביום מסוים.

**פרמטרים:**

- `date` (datetime.date, optional): התאריך לסיכום. ברירת מחדל: היום

**מחזיר:**

```python
{
    "date": "2025-01-15",
    "feedings": {
        "count": 8,
        "total_duration_minutes": 180.0,
        "total_amount": 800.0
    },
    "sleep": {
        "count": 5,
        "total_duration_minutes": 720.0,
        "total_duration_hours": 12.0,
        "naps": 3
    },
    "diapers": {
        "count": 9,
        "wet": 7,
        "solid": 4
    }
}
```

---

#### `get_current_status()`

**המצב הנוכחי המלא** - מה קרה לאחרונה, מה צפוי, וסטטיסטיקות שבועיות.

**מחזיר:** מילון עם כל המידע:

- `last_feeding` - האכלה אחרונה
- `next_feeding_prediction` - חיזוי האכלה הבאה
- `last_sleep` - שינה אחרונה
- `next_sleep_prediction` - חיזוי שינה הבאה
- `last_diaper` - חיתול אחרון
- `stats_7_days` - סטטיסטיקות שבועיות

---

## Management Commands

פקודות שרצות מהטרמינל או דרך cron jobs.

### ⚙️ 1. backup_database

**גיבוי אוטומטי של כל בסיס הנתונים**

```bash
# גיבוי בסיסי
python manage.py backup_database

# גיבוי לתיקייה מסוימת
python manage.py backup_database --output-dir /backups/babybuddy

# גיבוי בפורמט XML
python manage.py backup_database --format xml
```

**פרמטרים:**

- `--output-dir` - תיקיית יעד (ברירת מחדל: `backups/`)
- `--format` - פורמט הגיבוי: `json` או `xml` (ברירת מחדל: `json`)

**מה זה עושה:**

- ✅ יוצר קובץ גיבוי עם timestamp
- ✅ גובה את כל המודלים (Children, Feedings, Sleep, וכו')
- ✅ יוצר קובץ metadata עם פרטים
- ✅ מציג סיכום של הגיבוי

**דוגמת פלט:**

```
מתחיל גיבוי... / Starting backup...
  ✓ Children: 2 רשומות
  ✓ Feedings: 156 רשומות
  ✓ Sleep: 98 רשומות
  ✓ Diaper Changes: 189 רשומות
  ...

✅ גיבוי הושלם בהצלחה!
   קובץ: backups/babybuddy_backup_20250115_143022.json
   גודל: 2.34 MB
   סה"כ רשומות: 512
   מטא-דאטה: backups/babybuddy_backup_20250115_143022_metadata.json
```

**Cron Job לגיבוי יומי:**

```cron
# כל יום ב-2 בלילה
0 2 * * * cd /path/to/babybuddy && python manage.py backup_database
```

---

### 📊 2. daily_summary

**הצג סיכום יומי של פעילויות התינוק**

```bash
# סיכום של היום
python manage.py daily_summary

# סיכום של ילד ספציפי
python manage.py daily_summary --child baby-slug

# סיכום של תאריך מסוים
python manage.py daily_summary --date 2025-01-14

# סיכום של 3 ימים אחרונים
python manage.py daily_summary --days 3
```

**פרמטרים:**

- `--child` - slug או שם של הילד
- `--date` - תאריך בפורמט YYYY-MM-DD
- `--days` - מספר ימים לסיכום (ברירת מחדל: 1)

**דוגמת פלט:**

```
============================================================
📊 סיכום יומי עבור Emma | Daily Summary for Emma
============================================================

📅 Tuesday, 2025-01-14
------------------------------------------------------------

🍼 האכלות / Feedings:
   • מספר: 8
   • משך כולל: 185.5 דקות
   • כמות כוללת: 950 ml

💤 שינה / Sleep:
   • מספר תקופות שינה: 5
   • תנומות: 3
   • שינה כוללת: 12.5 שעות (750 דקות)

🧷 חיתולים / Diapers:
   • סה"כ: 9
   • רטובים: 7
   • מוצקים: 4

============================================================
📈 סטטיסטיקות 7 ימים אחרונים
============================================================

🍼 האכלות:
   • ממוצע בין האכלות: 180.0 דקות
   • ממוצע משך האכלה: 23.5 דקות
   • סה"כ האכלות: 56

💤 שינה:
   • ממוצע שעות שינה ביום: 13.2 שעות
   • ממוצע משך תנומה: 45.0 דקות
   • סה"כ תנומות: 21

============================================================
🔮 חיזויים / Predictions
============================================================

🍼 האכלה הבאה:
   בקרוב! בעוד ~25 דקות
   זמן משוער: 14:30

💤 שינה הבאה:
   התינוק מתחיל להתעייף - בעוד ~15 דקות

============================================================
✅ סיכום הושלם / Summary completed
============================================================
```

**שימוש ב-Cron לדוח בוקר:**

```cron
# כל יום ב-8 בבוקר - שלח דוא"ל עם סיכום
0 8 * * * cd /path/to/babybuddy && python manage.py daily_summary | mail -s "Baby Summary" parent@example.com
```

---

### 👶 3. child_status

**הצג מצב נוכחי של התינוק - מה קרה לאחרונה ומה צפוי**

```bash
# מצב של הילד הראשון במערכת
python manage.py child_status

# מצב של ילד ספציפי
python manage.py child_status --child emma
```

**דוגמת פלט:**

```
======================================================================
👶 מצב נוכחי של Emma | Current Status of Emma
🕐 Tuesday, 14 January 2025 - 14:25
======================================================================

🍼 האכלה אחרונה / Last Feeding:
   ⏱️  לפני 2:15 שעות
   📋 סוג: breast milk
   💧 כמות: 150 ml

🔮 האכלה הבאה / Next Feeding Prediction:
   ⏰ בקרוב! בעוד ~15 דקות
   🕐 זמן משוער: 14:40

----------------------------------------------------------------------

💤 שינה אחרונה / Last Sleep:
   ⏱️  התעורר לפני 1:30 שעות
   ⌛ משך: 45 דקות
   🌙 סוג: תנומה / Nap

🔮 שינה הבאה / Next Sleep Prediction:
   ⏰ ער כבר 90 דקות
   😴 התינוק מתחיל להתעייף - בעוד ~10 דקות

----------------------------------------------------------------------

🧷 חיתול אחרון / Last Diaper Change:
   ⏱️  לפני 1:45 שעות
   📋 רטוב / Wet

======================================================================
📊 סטטיסטיקות 7 ימים אחרונים / Last 7 Days Stats
======================================================================

🍼 האכלות:
   • 56 האכלות
   • ממוצע בין האכלות: 180 דקות
   • ממוצע משך האכלה: 24 דקות

💤 שינה:
   • ממוצע 13.2 שעות ביום
   • 21 תנומות
   • ממוצע תנומה: 45 דקות

🧷 חיתולים:
   • 63 חיתולים
   • ממוצע: 9.0 ביום

======================================================================
✅ סיכום מצב הושלם / Status summary completed
======================================================================
```

**שימוש מהיר:**

```bash
# בדוק מצב במהירות
watch -n 300 'python manage.py child_status'  # רענן כל 5 דקות
```

---

## API Endpoints

כל ה-endpoints דורשים authentication (כניסה למערכת).

### Base URL

```
/api/analytics/
```

---

### 📊 1. Child Analytics

**GET** `/api/analytics/child/<child_slug>/`

סטטיסטיקות כלליות על ילד.

**Query Parameters:**

- `days` (optional): מספר ימים (ברירת מחדל: 7)

**דוגמה:**

```bash
curl -X GET "http://localhost:8000/api/analytics/child/emma/?days=7" \
     -H "Authorization: Token YOUR_TOKEN"
```

**Response:**

```json
{
  "child": {
    "name": "Emma Smith",
    "slug": "emma",
    "birth_date": "2024-10-15"
  },
  "feeding_stats": {
    "count": 56,
    "average_duration_minutes": 23.5,
    "average_interval_minutes": 180.0,
    "total_amount": 850.0,
    "by_type": {
      "breast milk": 40,
      "formula": 16
    },
    "period_days": 7
  },
  "sleep_stats": {
    "count": 35,
    "total_sleep_hours": 92.3,
    "average_sleep_hours_per_day": 13.2,
    "naps_count": 21,
    "night_sleep_count": 14,
    "average_nap_duration_minutes": 45.0,
    "period_days": 7
  },
  "diaper_stats": {
    "count": 63,
    "wet_count": 52,
    "solid_count": 35,
    "average_per_day": 9.0,
    "period_days": 7
  }
}
```

---

### 👶 2. Current Status

**GET** `/api/analytics/child/<child_slug>/status/`

מצב נוכחי מלא - מה קרה לאחרונה ומה צפוי.

**Response:**

```json
{
  "child": {
    "name": "Emma Smith",
    "slug": "emma"
  },
  "timestamp": "2025-01-14T14:25:00Z",
  "last_feeding": {
    "time_since_minutes": 135.0,
    "time_since_hours": 2.25,
    "time_since_formatted": "2:15",
    "type": "breast milk",
    "amount": 150.0,
    "end_time": "2025-01-14T12:10:00Z"
  },
  "next_feeding_prediction": {
    "status": "soon",
    "message": "בקרוב! בעוד ~15 דקות",
    "minutes_until_next": 15.0,
    "estimated_time": "2025-01-14T14:40:00Z",
    "average_interval_minutes": 180.0,
    "confidence": "high"
  },
  "last_sleep": {
    "time_since_minutes": 90.0,
    "time_since_hours": 1.5,
    "time_since_formatted": "1:30",
    "was_nap": true,
    "duration_minutes": 45.0,
    "end_time": "2025-01-14T12:55:00Z"
  },
  "next_sleep_prediction": {
    "status": "getting_tired",
    "message": "התינוק מתחיל להתעייף - בעוד ~10 דקות",
    "minutes_awake": 90.0,
    "minutes_until_tired": 10.0,
    "typical_wake_window_minutes": 90
  },
  "last_diaper": {
    "time_since_minutes": 105.0,
    "time_since_hours": 1.75,
    "time_since_formatted": "1:45",
    "was_wet": true,
    "was_solid": false,
    "time": "2025-01-14T12:40:00Z"
  },
  "stats_7_days": {
    "feeding": {
      /* ... */
    },
    "sleep": {
      /* ... */
    },
    "diapers": {
      /* ... */
    }
  }
}
```

---

### 📅 3. Daily Summary

**GET** `/api/analytics/child/<child_slug>/daily/`

סיכום יומי של פעילויות.

**Query Parameters:**

- `date` (optional): תאריך בפורמט YYYY-MM-DD (ברירת מחדל: היום)

**דוגמה:**

```bash
curl -X GET "http://localhost:8000/api/analytics/child/emma/daily/?date=2025-01-14"
```

**Response:**

```json
{
  "child": {
    "name": "Emma Smith",
    "slug": "emma"
  },
  "summary": {
    "date": "2025-01-14",
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
  }
}
```

---

### 🔮 4. Predict Feeding

**GET** `/api/analytics/child/<child_slug>/predict-feeding/`

חיזוי האכלה הבאה.

**Response:**

```json
{
  "child": {
    "name": "Emma Smith",
    "slug": "emma"
  },
  "prediction": {
    "status": "soon",
    "message": "בקרוב! בעוד ~15 דקות",
    "minutes_until_next": 15.0,
    "estimated_time": "2025-01-14T14:40:00Z",
    "average_interval_minutes": 180.0,
    "confidence": "high"
  }
}
```

---

### 🔮 5. Predict Sleep

**GET** `/api/analytics/child/<child_slug>/predict-sleep/`

חיזוי שינה הבאה.

**Response:**

```json
{
  "child": {
    "name": "Emma Smith",
    "slug": "emma"
  },
  "prediction": {
    "status": "getting_tired",
    "message": "התינוק מתחיל להתעייף - בעוד ~10 דקות",
    "minutes_awake": 90.0,
    "minutes_until_tired": 10.0,
    "typical_wake_window_minutes": 90
  }
}
```

---

### 👥 6. All Children Status

**GET** `/api/analytics/all-children/`

מצב של כל הילדים במערכת (שימושי לבתים עם כמה ילדים).

**Response:**

```json
{
  "children": [
    {
      "name": "Emma Smith",
      "slug": "emma",
      "last_feeding_minutes_ago": 135.0,
      "last_sleep_minutes_ago": 90.0,
      "next_feeding_status": "soon",
      "next_feeding_message": "בקרוב! בעוד ~15 דקות"
    },
    {
      "name": "Noah Johnson",
      "slug": "noah",
      "last_feeding_minutes_ago": 85.0,
      "last_sleep_minutes_ago": 180.0,
      "next_feeding_status": "later",
      "next_feeding_message": "בעוד ~1.5 שעות"
    }
  ],
  "count": 2
}
```

---

## דוגמאות שימוש

### Python Script

```python
import requests

# הגדרות
BASE_URL = "http://localhost:8000"
TOKEN = "your-api-token-here"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# קבל מצב נוכחי
response = requests.get(
    f"{BASE_URL}/api/analytics/child/emma/status/",
    headers=HEADERS
)
status = response.json()

# בדוק אם הגיע זמן להאכלה
feeding_pred = status['next_feeding_prediction']
if feeding_pred and feeding_pred['status'] in ['overdue', 'soon']:
    print(f"⚠️ התראה: {feeding_pred['message']}")

# בדוק אם התינוק עייף
sleep_pred = status['next_sleep_prediction']
if sleep_pred and sleep_pred['status'] == 'overtired':
    print(f"😴 התראה: {sleep_pred['message']}")
```

---

### JavaScript / Node.js

```javascript
const axios = require("axios");

const BASE_URL = "http://localhost:8000";
const TOKEN = "your-api-token-here";

async function checkBabyStatus(childSlug) {
  try {
    const response = await axios.get(
      `${BASE_URL}/api/analytics/child/${childSlug}/status/`,
      {
        headers: { Authorization: `Token ${TOKEN}` },
      },
    );

    const status = response.data;

    // הצג מצב נוכחי
    console.log(`👶 ${status.child.name}`);

    if (status.next_feeding_prediction) {
      const { status: feedStatus, message } = status.next_feeding_prediction;
      console.log(`🍼 ${message}`);

      if (feedStatus === "overdue") {
        // שלח התראה
        sendNotification("התינוק רעב!", message);
      }
    }

    return status;
  } catch (error) {
    console.error("Error:", error.message);
  }
}

// בדוק כל 5 דקות
setInterval(() => checkBabyStatus("emma"), 5 * 60 * 1000);
```

---

### Shell Script לגיבוי אוטומטי

```bash
#!/bin/bash
# backup_babybuddy.sh

cd /path/to/babybuddy

# גיבוי
python manage.py backup_database --output-dir /backups/babybuddy

# מחק גיבויים ישנים (יותר מ-30 יום)
find /backups/babybuddy -name "*.json" -mtime +30 -delete

# שלח הודעה
echo "Baby Buddy backup completed at $(date)" | mail -s "Backup Success" admin@example.com
```

הוסף ל-crontab:

```cron
0 2 * * * /path/to/backup_babybuddy.sh
```

---

## התקנה ושימוש

### דרישות מקדימות

- Django 5.x
- Python 3.11+
- Baby Buddy מותקן ופועל

### שלבי התקנה

כל הקבצים כבר בפרויקט! פשוט:

1. **ודא שהקבצים קיימים:**

   ```bash
   ls core/analytics.py
   ls core/management/commands/
   ls api/analytics_views.py
   ```

2. **הרץ migrations (אם צריך):**

   ```bash
   python manage.py migrate
   ```

3. **נסה את הפקודות:**

   ```bash
   # מצב נוכחי
   python manage.py child_status

   # סיכום יומי
   python manage.py daily_summary

   # גיבוי
   python manage.py backup_database
   ```

4. **נסה את ה-API:**

   ```bash
   # קבל token (אם אין לך)
   python manage.py drf_create_token your_username

   # נסה endpoint
   curl -H "Authorization: Token YOUR_TOKEN" \
        http://localhost:8000/api/analytics/child/CHILD_SLUG/status/
   ```

---

## שיפורים עתידיים / Future Improvements

רעיונות לפיתוח עתידי:

- [ ] **Machine Learning** - חיזוי מתקדם יותר עם scikit-learn
- [ ] **התראות אוטומטיות** - Email/SMS/Push notifications
- [ ] **דוחות PDF** - ייצוא סיכומים ל-PDF עם גרפים
- [ ] **גרפים אינטראקטיביים** - Plotly/Chart.js בממשק
- [ ] **שילוב עם Home Assistant** - אוטומציה של הבית
- [ ] **אפליקציית מובייל** - React Native / Flutter
- [ ] **חיזוי לפי גיל** - התאמת wake windows לגיל התינוק
- [ ] **מצב משפחה** - שיתוף בין הורים עם התראות

---

## תרומה / Contributing

רוצה לשפר? יצרת משהו מגניב?

1. Fork the repository
2. Create feature branch
3. Commit your changes
4. Push to the branch
5. Create Pull Request

---

## License

BSD-2-Clause (כמו Baby Buddy המקורי)

---

## תמיכה / Support

- 📖 [Baby Buddy Docs](https://docs.baby-buddy.net)
- 💬 [GitHub Issues](https://github.com/babybuddy/babybuddy/issues)
- 🗨️ [Gitter Chat](https://gitter.im/babybuddy/Lobby)

---

**נבנה עם ❤️ לקראת הלידה של התינוקת! 👶**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
