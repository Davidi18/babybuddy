# 🌊 Windsurf Context - Baby Buddy Analytics & Webhooks
# הקשר עבור Windsurf - תכונות חדשות ב-Baby Buddy

> מסמך זה מיועד לעורך Windsurf כדי להבין את השינויים והתוספות החדשות שנוספו לפרויקט Baby Buddy.

---

## 🎯 סיכום מהיר - מה נוסף לפרויקט

הוספנו למערכת Baby Buddy **מערכת אנליטיקה וחיזויים מלאה** כולל:

1. **📊 Analytics Module** - לוגיקה לניתוח דפוסים וחיזוי התנהגות התינוק
2. **⚙️ Management Commands** - 3 פקודות ניהול שימושיות
3. **🔌 API Endpoints** - 6 endpoints חדשים לסטטיסטיקות
4. **🔗 Webhooks** - 3 webhooks לשילוב עם n8n/Zapier
5. **📖 תיעוד מלא** - 3 מסמכי README מפורטים

**⚠️ חשוב:** כל התוספות הן **backend בלבד** - אין שינויי UI! רק לוגיקה, API, ופקודות.

---

## 📁 מבנה הקבצים החדשים

### קבצים חדשים שנוצרו:

```
babybuddy/
├── core/
│   ├── analytics.py                         ⭐ NEW - מוח המערכת
│   └── management/
│       ├── __init__.py                      ⭐ NEW
│       └── commands/
│           ├── __init__.py                  ⭐ NEW
│           ├── backup_database.py           ⭐ NEW - גיבוי אוטומטי
│           ├── daily_summary.py             ⭐ NEW - סיכום יומי
│           └── child_status.py              ⭐ NEW - מצב נוכחי
│
├── api/
│   ├── analytics_views.py                   ⭐ NEW - 6 API endpoints
│   ├── webhook_views.py                     ⭐ NEW - 3 webhooks
│   └── urls.py                              ✏️ MODIFIED - נוספו routes
│
├── ANALYTICS_FEATURES.md                    ⭐ NEW - תיעוד מלא
├── N8N_WEBHOOKS_GUIDE.md                    ⭐ NEW - מדריך webhooks
└── WINDSURF_CONTEXT.md                      ⭐ NEW - מסמך זה
```

---

## 🧮 core/analytics.py - המוח של המערכת

### מה יש בקובץ:

**מחלקה מרכזית:** `BabyAnalytics(child)`

זו מחלקה שמקבלת אובייקט `Child` ומספקת כל הפונקציונליות של אנליטיקה.

### Structure:

```python
class BabyAnalytics:
    def __init__(self, child):
        self.child = child

    # === Feeding Analytics ===
    def get_feeding_stats(days=7) -> Dict
    def get_last_feeding_info() -> Optional[Dict]
    def predict_next_feeding() -> Optional[Dict]  # 🔮 חיזוי!

    # === Sleep Analytics ===
    def get_sleep_stats(days=7) -> Dict
    def get_last_sleep_info() -> Optional[Dict]
    def predict_next_sleep() -> Optional[Dict]    # 🔮 חיזוי!

    # === Diaper Analytics ===
    def get_diaper_stats(days=7) -> Dict
    def get_last_diaper_info() -> Optional[Dict]

    # === Combined ===
    def get_daily_summary(date=None) -> Dict
    def get_current_status() -> Dict              # הכל ביחד!
```

### לוגיקת החיזוי:

#### **Feeding Prediction:**
```python
# לוגיקה פשוטה:
# 1. חשב ממוצע מרווח בין האכלות (7 ימים)
# 2. בדוק כמה זמן עבר מהאכלה אחרונה
# 3. חזה: זמן_להאכלה_הבאה = ממוצע - זמן_שעבר

# סטטוסים:
# - "overdue": עבר הזמן, התינוק רעב!
# - "soon": בעוד פחות מ-30 דקות
# - "upcoming": בעוד 30-60 דקות
# - "later": בעוד יותר משעה
```

#### **Sleep Prediction:**
```python
# משתמש ב-"wake window" - זמן טיפוסי שתינוק יכול להיות ער
# ברירת מחדל: 90 דקות (ניתן לשיפור לפי גיל)

# סטטוסים:
# - "overtired": עבר הזמן, עייף מאוד
# - "getting_tired": מתחיל להתעייף
# - "soon": בקרוב יתעייף
# - "awake": עוד לא עייף
```

### דוגמאות שימוש:

```python
from core.models import Child
from core.analytics import BabyAnalytics

# קבל ילד
child = Child.objects.get(slug='emma')

# צור instance
analytics = BabyAnalytics(child)

# קבל סטטיסטיקות
feeding_stats = analytics.get_feeding_stats(days=7)
# → {"count": 56, "average_interval_minutes": 180.0, ...}

# חזה האכלה הבאה
prediction = analytics.predict_next_feeding()
# → {"status": "soon", "message": "בקרוב! בעוד ~15 דקות", ...}

# מצב נוכחי מלא
status = analytics.get_current_status()
# → {"last_feeding": {...}, "next_feeding_prediction": {...}, ...}
```

---

## ⚙️ Management Commands

3 פקודות Django שרצות מהטרמינל:

### 1. `child_status`
```bash
python manage.py child_status [--child=emma]
```
**מה זה עושה:**
- מציג מצב נוכחי של התינוק
- מה קרה לאחרונה (האכלה, שינה, חיתול)
- מה צפוי בקרוב (חיזויים)
- סטטיסטיקות שבועיות

**Output:** טקסט מעוצב לטרמינל עם emojis.

---

### 2. `daily_summary`
```bash
python manage.py daily_summary [--child=emma] [--date=2025-01-15] [--days=1]
```
**מה זה עושה:**
- סיכום יומי של כל הפעילויות
- האכלות, שינה, חיתולים
- סטטיסטיקות שבועיות
- חיזויים

**Use case:** שליחה במייל כל בוקר (cron job).

---

### 3. `backup_database`
```bash
python manage.py backup_database [--output-dir=backups] [--format=json]
```
**מה זה עושה:**
- גיבוי מלא של כל בסיס הנתונים
- יוצר קובץ JSON/XML עם כל המודלים
- יוצר metadata file
- מתאים לגיבויים אוטומטיים

---

## 🔌 API Endpoints - analytics_views.py

6 endpoints חדשים תחת `/api/analytics/`:

### Structure:
```python
# כל ה-views הם Class-based או Function-based
# כולם דורשים Authentication (IsAuthenticated)

class ChildAnalyticsView(APIView)           # GET /api/analytics/child/<slug>/
class ChildCurrentStatusView(APIView)       # GET /api/analytics/child/<slug>/status/
class ChildDailySummaryView(APIView)        # GET /api/analytics/child/<slug>/daily/
class ChildFeedingPredictionView(APIView)   # GET /api/analytics/child/<slug>/predict-feeding/
class ChildSleepPredictionView(APIView)     # GET /api/analytics/child/<slug>/predict-sleep/
class AllChildrenStatusView(APIView)        # GET /api/analytics/all-children/
```

### דוגמת שימוש:

```bash
# קבל מצב נוכחי
curl -H "Authorization: Token YOUR_TOKEN" \
     https://baby.example.com/api/analytics/child/emma/status/

# Response:
{
  "child": {"name": "Emma", "slug": "emma"},
  "last_feeding": {
    "time_since_minutes": 135.0,
    "type": "breast milk",
    "amount": 150.0
  },
  "next_feeding_prediction": {
    "status": "soon",
    "message": "בקרוב! בעוד ~15 דקות",
    "estimated_time": "2025-01-15T14:40:00Z"
  },
  ...
}
```

---

## 🔗 Webhooks - webhook_views.py

3 webhook endpoints תחת `/api/webhooks/`:

### מיוחדים לאוטומציה (n8n, Zapier, Make)!

```python
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def daily_summary_webhook(request)    # /api/webhooks/daily-summary/

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def status_webhook(request)           # /api/webhooks/status/

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def alerts_webhook(request)           # /api/webhooks/alerts/
```

### מה זה עושה:

1. **daily_summary_webhook:**
   - מחזיר סיכום יומי **בפורמט טקסט מעוצב**
   - השדה `message` מוכן לשליחה בWhatsApp/Telegram!
   - כולל: נתוני היום, ממוצעים, חיזויים, התראות

2. **status_webhook:**
   - מצב נוכחי קצר ותמציתי
   - `status_text` - משפט אחד עם הכל
   - מתאים לבדיקות תכופות (כל 5-15 דקות)

3. **alerts_webhook:**
   - מחזיר תוצאה **רק אם יש התראה דחופה**!
   - `has_alerts`: true/false
   - מתאים לשליחת התראות בזמן אמת

### Response מיוחד:

```json
{
  "success": true,
  "message": "📊 סיכום יומי - Emma\n📅 15/01/2025\n\n🍼 האכלות היום:\n  • 8 האכלות\n...",
  "data": { /* JSON מובנה */ },
  "alerts": [ /* array של התראות */ ]
}
```

**השדה `message`** - זה הקסם! טקסט מוכן לשליחה ישירות.

---

## 🔄 api/urls.py - השינויים

### מה שהתוסף:

```python
from . import analytics_views
from . import webhook_views

urlpatterns = [
    # ... הקיים ...

    # ===== Analytics Endpoints =====
    path("api/analytics/child/<slug:child_slug>/", ...),
    path("api/analytics/child/<slug:child_slug>/status/", ...),
    path("api/analytics/child/<slug:child_slug>/daily/", ...),
    path("api/analytics/child/<slug:child_slug>/predict-feeding/", ...),
    path("api/analytics/child/<slug:child_slug>/predict-sleep/", ...),
    path("api/analytics/all-children/", ...),

    # ===== Webhook Endpoints =====
    path("api/webhooks/daily-summary/", ...),
    path("api/webhooks/status/", ...),
    path("api/webhooks/alerts/", ...),
]
```

**חשוב:** כל ה-routes החדשים תחת `/api/` - לא משנים routes קיימים!

---

## 🎨 אם Windsurf רוצה לעשות UI...

### כאן האפשרויות:

#### **1. Dashboard Page חדש:**

מקום מומלץ: `dashboard/templates/dashboard/`

דף חדש עם:
- 📊 גרפים של סטטיסטיקות
- 🔮 חיזויים בזמן אמת
- ⏰ טיימליין של אירועים
- 📈 טרנדים

#### **2. Widget בעמוד הבית:**

להוסיף ל-`dashboard/templates/dashboard/child.html`:

```django
{% load static %}

<div class="analytics-widget">
  <h3>🔮 חיזוי האכלה הבאה</h3>
  <div id="next-feeding-prediction">
    <!-- JavaScript יטען את הנתונים מ-API -->
  </div>
</div>

<script>
fetch('/api/analytics/child/{{ child.slug }}/predict-feeding/', {
  headers: {
    'Authorization': 'Token {{ request.user.auth_token }}'
  }
})
.then(res => res.json())
.then(data => {
  document.getElementById('next-feeding-prediction').innerHTML =
    `<p>${data.prediction.message}</p>
     <p>זמן משוער: ${new Date(data.prediction.estimated_time).toLocaleTimeString('he-IL')}</p>`;
});
</script>
```

#### **3. Real-time Status Bar:**

Header עליון עם מצב נוכחי:

```django
<div class="status-bar">
  <span>🍼 האכלה אחרונה: <span id="last-feeding">טוען...</span></span>
  <span>💤 ער: <span id="awake-time">טוען...</span></span>
  <span id="next-alert" class="alert"></span>
</div>

<script>
// רענון כל 5 דקות
setInterval(async () => {
  const res = await fetch('/api/webhooks/status/?child={{ child.slug }}', {
    headers: {'Authorization': 'Token {{ request.user.auth_token }}'}
  });
  const data = await res.json();

  document.getElementById('last-feeding').textContent =
    data.last_feeding_minutes_ago ? `לפני ${Math.round(data.last_feeding_minutes_ago)} דקות` : 'N/A';

  // הצג התראה אם יש
  if (data.alerts.length > 0) {
    document.getElementById('next-alert').textContent = data.alerts[0].message;
    document.getElementById('next-alert').classList.add('warning');
  }
}, 5 * 60 * 1000);
</script>
```

---

## 📊 דוגמאות לקוד שWindsurf יכול להשתמש בו

### View Function דוגמה:

```python
# dashboard/views.py
from django.shortcuts import render
from core.models import Child
from core.analytics import BabyAnalytics

def analytics_dashboard(request, slug):
    """דף אנליטיקה חדש"""
    child = get_object_or_404(Child, slug=slug)
    analytics = BabyAnalytics(child)

    context = {
        'child': child,
        'status': analytics.get_current_status(),
        'daily_summary': analytics.get_daily_summary(),
        'feeding_stats': analytics.get_feeding_stats(days=7),
        'sleep_stats': analytics.get_sleep_stats(days=7),
    }

    return render(request, 'dashboard/analytics.html', context)
```

### Template דוגמה:

```django
{% extends "babybuddy/base.html" %}
{% load i18n %}

{% block title %}{% trans "Analytics" %} - {{ child }}{% endblock %}

{% block content %}
<div class="container">
  <h1>📊 {% trans "Analytics Dashboard" %} - {{ child.name }}</h1>

  <div class="row">
    <div class="col-md-6">
      <div class="card">
        <h3>🍼 {% trans "Next Feeding Prediction" %}</h3>
        {% if status.next_feeding_prediction %}
          <p class="prediction-message">{{ status.next_feeding_prediction.message }}</p>
          <p class="prediction-time">
            {% trans "Estimated time:" %}
            {{ status.next_feeding_prediction.estimated_time|date:"H:i" }}
          </p>

          {% if status.next_feeding_prediction.status == "overdue" %}
            <div class="alert alert-danger">⚠️ {% trans "Baby is hungry!" %}</div>
          {% elif status.next_feeding_prediction.status == "soon" %}
            <div class="alert alert-warning">⏰ {% trans "Soon!" %}</div>
          {% endif %}
        {% else %}
          <p>{% trans "Not enough data for prediction" %}</p>
        {% endif %}
      </div>
    </div>

    <div class="col-md-6">
      <div class="card">
        <h3>💤 {% trans "Sleep Status" %}</h3>
        {% if status.last_sleep %}
          <p>{% trans "Awake for:" %} {{ status.last_sleep.time_since_formatted }}</p>
          <p>{% trans "Last sleep duration:" %} {{ status.last_sleep.duration_minutes|floatformat:0 }} {% trans "minutes" %}</p>

          {% if status.next_sleep_prediction %}
            <p class="prediction-message">{{ status.next_sleep_prediction.message }}</p>
          {% endif %}
        {% endif %}
      </div>
    </div>
  </div>

  <div class="row mt-4">
    <div class="col-md-12">
      <div class="card">
        <h3>📅 {% trans "Today's Summary" %}</h3>
        <ul>
          <li>🍼 {% trans "Feedings:" %} {{ daily_summary.feedings.count }}</li>
          <li>💤 {% trans "Sleep:" %} {{ daily_summary.sleep.total_duration_hours }} {% trans "hours" %}</li>
          <li>🧷 {% trans "Diapers:" %} {{ daily_summary.diapers.count }}</li>
        </ul>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

## 🎯 כיוונים מומלצים ל-Windsurf

### מה כדאי לבנות ב-UI:

#### **1. סטטוס נוכחי בעמוד הבית** ⭐ Priority 1
- קטע קטן עם "מה קרה לאחרונה + מה צפוי"
- מקום: בראש דף הילד
- API: `/api/webhooks/status/`

#### **2. דף אנליטיקה מלא** ⭐ Priority 2
- דף חדש עם כל הסטטיסטיקות
- גרפים (Plotly/Chart.js כבר בפרויקט!)
- טבלאות
- API: `/api/analytics/child/<slug>/`

#### **3. התראות בזמן אמת** ⭐ Priority 3
- Toast notifications כשהתינוק רעב/עייף
- Polling כל 5 דקות
- API: `/api/webhooks/alerts/`

#### **4. Timeline View** 💡 Nice to have
- טיימליין חזותי של היום
- "האכלה → שינה → חיתול → האכלה..."
- חיזויים מסומנים בקו זמן

---

## 🚨 דברים חשובים לדעת

### **1. Authentication:**
```python
# כל ה-API endpoints דורשים authentication
# בתבניות Django:
headers = {
    'Authorization': f'Token {request.user.auth_token.key}'
}

# ב-JavaScript:
fetch(url, {
  headers: {
    'Authorization': 'Token ' + userToken
  }
})
```

### **2. Child Slug:**
```python
# כל הendpoints משתמשים ב-slug, לא ב-id
# טוב: /api/analytics/child/emma/
# לא טוב: /api/analytics/child/1/

# קבלת slug בtemplate:
{{ child.slug }}
```

### **3. Date Formats:**
```python
# API מחזיר ISO 8601:
"estimated_time": "2025-01-15T14:40:00Z"

# להציג יפה בtemplate:
{{ prediction.estimated_time|date:"H:i" }}
```

### **4. Hebrew Support:**
```django
{% load i18n %}
{% trans "Feeding" %}  <!-- יתורגם לעברית אם המערכת בעברית -->
```

### **5. Error Handling:**
```javascript
fetch('/api/webhooks/status/')
  .then(res => {
    if (!res.ok) throw new Error('Failed to fetch');
    return res.json();
  })
  .then(data => {
    // עבד
  })
  .catch(error => {
    console.error('Error:', error);
    // הצג הודעת שגיאה למשתמש
  });
```

---

## 📚 קבצי תיעוד נוספים

1. **ANALYTICS_FEATURES.md** - תיעוד מלא של כל הפיצ'רים
2. **N8N_WEBHOOKS_GUIDE.md** - מדריך webhooks ל-n8n
3. **ADMIN_RESET.md** - ניהול superuser
4. **DEPLOY.md** - הנחיות deployment
5. **COOLIFY_SETUP.md** - מדריך Coolify מפורט

---

## 🛠️ Dev Tools

### בדיקות מהירות:

```bash
# הרץ management command
python manage.py child_status

# בדוק API endpoint
curl http://localhost:8000/api/webhooks/status/ \
     -H "Authorization: Token YOUR_TOKEN"

# צור token למשתמש
python manage.py drf_create_token your_username
```

### Django Shell:

```python
python manage.py shell

>>> from core.models import Child
>>> from core.analytics import BabyAnalytics
>>>
>>> child = Child.objects.first()
>>> analytics = BabyAnalytics(child)
>>>
>>> # נסה פונקציה
>>> status = analytics.get_current_status()
>>> print(status['next_feeding_prediction'])
```

---

## 🎨 UI Guidelines

### עיצוב מומלץ:

**כרטיסי חיזוי:**
```html
<div class="prediction-card {{ prediction.status }}">
  <!-- status classes: overdue, soon, upcoming, later -->
  <div class="prediction-icon">🍼</div>
  <div class="prediction-content">
    <h4>האכלה הבאה</h4>
    <p class="message">{{ prediction.message }}</p>
    <time>{{ prediction.estimated_time|date:"H:i" }}</time>
  </div>
</div>
```

**CSS מומלץ:**
```css
.prediction-card {
  border-left: 4px solid #ccc;
  padding: 1rem;
  margin: 1rem 0;
}

.prediction-card.overdue {
  border-color: #dc3545;
  background: #fff5f5;
}

.prediction-card.soon {
  border-color: #ffc107;
  background: #fffbf0;
}

.prediction-card.upcoming {
  border-color: #17a2b8;
  background: #f0f9ff;
}
```

---

## 🔍 מה לחפש בקוד הקיים

### Models רלוונטיים:
```python
# core/models.py
class Child(models.Model)           # הילד
class Feeding(models.Model)         # האכלות
class Sleep(models.Model)           # שינה
class DiaperChange(models.Model)    # חיתולים
class Timer(models.Model)           # טיימרים
```

### Views קיימים:
```python
# dashboard/views.py
class ChildList(...)        # רשימת ילדים
class ChildDetail(...)      # פרטי ילד
```

### Templates קיימים:
```
dashboard/templates/dashboard/
├── child.html              # דף הילד הראשי
├── child_list.html         # רשימת ילדים
└── ...
```

---

## 🚀 Quick Start ל-Windsurf

### אם רוצה להוסיף Status Widget מהיר:

**1. ב-`dashboard/templates/dashboard/child.html`:**

מצא איפה שמתאים (למשל אחרי הכותרת), והוסף:

```django
<div class="analytics-status-bar">
  <div id="status-loading">טוען מצב...</div>
  <div id="status-content" style="display:none;">
    <span id="status-text"></span>
  </div>
</div>

<script>
(async function() {
  try {
    const res = await fetch('/api/webhooks/status/?child={{ child.slug }}', {
      headers: {'Authorization': 'Token {{ request.user.auth_token.key }}'}
    });
    const data = await res.json();

    document.getElementById('status-loading').style.display = 'none';
    document.getElementById('status-content').style.display = 'block';
    document.getElementById('status-text').textContent = data.status_text;

    // צבע התראה אם צריך
    if (data.alerts.length > 0) {
      document.getElementById('status-content').classList.add('alert', 'alert-warning');
    }
  } catch(e) {
    console.error('Failed to load status:', e);
  }
})();
</script>
```

**זהו! זה יעבוד מיד.**

---

## ❓ שאלות נפוצות

### **Q: איך להציג חיזוי בעברית בtemplate?**
```django
{% if prediction %}
  <p>{{ prediction.message }}</p>  <!-- ההודעה כבר בעברית! -->
{% endif %}
```

### **Q: איך לרענן נתונים בזמן אמת?**
```javascript
setInterval(() => {
  fetch('/api/webhooks/status/?child=' + childSlug)
    .then(res => res.json())
    .then(updateUI);
}, 5 * 60 * 1000);  // כל 5 דקות
```

### **Q: איך לעשות גרף?**
Baby Buddy כבר משתמש ב-Plotly! ראה `reports/graphs/` לדוגמאות.

```python
# reports/graphs/your_new_graph.py
def feeding_prediction_graph(child):
    # יצירת גרף Plotly
    ...
```

---

## 🎉 סיכום ל-Windsurf

**מה יש לנו:**
- ✅ Backend מלא עם לוגיקת חיזוי
- ✅ API מוכן לשימוש
- ✅ Webhooks לאוטומציה חיצונית
- ⭐ **אין UI עדיין** - זה המשימה שלך!

**מה כדאי לבנות:**
1. Status widget בעמוד הילד
2. דף אנליטיקה מלא
3. התראות בזמן אמת
4. גרפים ווידג'טים

**איפה להתחיל:**
- `dashboard/templates/dashboard/child.html` - הוסף status bar
- API endpoints מוכנים - פשוט קרא אליהם!
- דוגמאות קוד למעלה - העתק והתאם

**זכור:**
- כל הAPI דורש authentication
- השתמש ב-`child.slug` ולא ב-`child.id`
- ה-`message` fields כבר בעברית!

---

**בהצלחה! 🌊 Windsurf, תעשה קסמים! ✨**

🤖 Generated with [Claude Code](https://claude.com/claude-code)
