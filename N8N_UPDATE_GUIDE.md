# מדריך עדכון Workflows ב-n8n

## Baby Buddy Webhooks - שינויים ועדכונים נדרשים

---

## 📋 סיכום השינויים

### ✅ מה השתנה:

1. **הודעות LLM חמודות ומגוונות** - כל ההודעות עכשיו בפורמט WhatsApp עם markdown
2. **עיצוב זמנים בעברית** - "שלוש שעות וחמש דקות" במקום "3.1 שעות"
3. **איחוד webhooks** - `smart-alerts` אוחד ל-`alerts` (endpoint אחד עם כל התכונות)
4. **סיכום יומי של אתמול** - `daily-summary` מראה אתמול בברירת מחדל (מתאים לבוקר)

### ⚠️ Breaking Changes:

- **נמחק**: `/api/webhooks/smart-alerts/` (הועבר ל-`/api/webhooks/alerts/`)

---

## 🔄 עדכונים נדרשים ל-Workflows

### 1️⃣ Daily Summary Workflow

**URL נוכחי**: `/api/webhooks/daily-summary/`
**סטטוס**: ✅ **עובד - מומלץ לעדכן פרמטרים**

#### מה השתנה:

- **ברירת מחדל חדשה**: מציג נתונים של **אתמול** (לא היום)
- **הודעות LLM**: ברירת מחדל `use_llm=true` - הודעות חמודות ומגוונות
- **פורמט WhatsApp**: markdown מובנה (_מודגש_, _נטוי_, אימוג'ים)

#### פרמטרים זמינים:

```
?child=נעמי-מאייר          # Child slug (ברירת מחדל: הילד הראשון)
&date=2025-01-15           # תאריך ספציפי (ברירת מחדל: אתמול)
&use_llm=true              # להשתמש ב-LLM (ברירת מחדל: true)
```

#### דוגמאות שימוש:

```bash
# סיכום של אתמול (ברירת מחדל)
GET https://baby.davidvmayer.com/api/webhooks/daily-summary/

# סיכום של תאריך ספציפי
GET https://baby.davidvmayer.com/api/webhooks/daily-summary/?date=2025-01-15

# סיכום עם הודעה גנרית (ללא LLM)
GET https://baby.davidvmayer.com/api/webhooks/daily-summary/?use_llm=false
```

#### מה לעדכן ב-n8n:

1. ✅ **אין צורך לעדכן URL**
2. 💡 **מומלץ**: הוסף פרמטר `use_llm=true` (אופציונלי, זה ברירת המחדל)
3. 💡 **מומלץ**: אם רצית נתוני היום - הוסף `date={{ $today.format('YYYY-MM-DD') }}`

---

### 2️⃣ Alerts Workflow (Smart Alerts)

**URL ישן**: `/api/webhooks/smart-alerts/` ❌ **נמחק**
**URL חדש**: `/api/webhooks/alerts/` ✅ **מאוחד**

#### מה השתנה:

- **איחוד מלא**: כל התכונות של smart-alerts עכשיו ב-`alerts`
- **הודעות LLM**: כל ההתראות עם הודעות חמודות ומגוונות
- **פורמט WhatsApp**: markdown אוטומטי לכל ההודעות
- **זמנים בעברית**: "שעתיים וחצי" במקום "2.5 hours"

#### פרמטרים זמינים (כולם אופציונליים):

```
?child=נעמי-מאייר               # Child slug
&feeding_threshold=15            # דקות איחור להתראת רעב (ברירת מחדל: 15)
&sleep_threshold=90              # דקות ערות להתראת עייפות (ברירת מחדל: 90)
&diaper_threshold=180            # דקות מחיתול אחרון (ברירת מחדל: 180)
&medication_threshold=0          # דקות לפני/אחרי תרופה (ברירת מחדל: 0)
&snooze_minutes=30               # דקות snooze בין התראות (ברירת מחדל: 30)
&quiet_hours_start=22            # שעה להתחלת שקט (ברירת מחדל: 22)
&quiet_hours_end=7               # שעה לסיום שקט (ברירת מחדל: 7)
&respect_quiet_hours=true        # לכבד שעות שקט (ברירת מחדל: true)
&use_llm=true                    # להשתמש ב-LLM (ברירת מחדל: true)
```

#### דוגמאות שימוש:

```bash
# התראות בסיסיות עם כל ברירות המחדל
GET https://baby.davidvmayer.com/api/webhooks/alerts/

# התראות מותאמות אישית
GET https://baby.davidvmayer.com/api/webhooks/alerts/?feeding_threshold=20&sleep_threshold=120

# התראות עם snooze ארוך יותר
GET https://baby.davidvmayer.com/api/webhooks/alerts/?snooze_minutes=60

# התראות בלי quiet hours
GET https://baby.davidvmayer.com/api/webhooks/alerts/?respect_quiet_hours=false
```

#### מה לעדכן ב-n8n:

1. ⚠️ **חובה**: שנה URL מ-`smart-alerts` ל-`alerts`
   ```
   מ:  https://baby.davidvmayer.com/api/webhooks/smart-alerts/
   ל:  https://baby.davidvmayer.com/api/webhooks/alerts/
   ```
2. ✅ כל הפרמטרים נשארו זהים
3. 💡 **מומלץ**: הוסף `use_llm=true` לקבלת הודעות חמודות

---

### 3️⃣ Status Webhook

**URL נוכחי**: `/api/webhooks/status/`
**סטטוס**: ✅ **ללא שינוי**

#### מה השתנה:

- **פורמט זמנים**: כל הזמנים עכשיו בעברית תקינה
  - `time_since_formatted` השתנה מ-`"3:06"` ל-`"שלוש שעות ו-5 דקות"`

#### פרמטרים:

```
?child=נעמי-מאייר          # Child slug (ברירת מחדל: הילד הראשון)
```

#### דוגמה:

```bash
GET https://baby.davidvmayer.com/api/webhooks/status/
```

#### מה לעדכן ב-n8n:

1. ✅ **אין צורך לעדכן URL**
2. 💡 **שים לב**: שדה `time_since_formatted` עכשיו בעברית (לא `HH:MM`)

---

### 4️⃣ Medications Webhook

**URL נוכחי**: `/api/webhooks/medications/`
**סטטוס**: ✅ **ללא שינוי**

#### פרמטרים:

```
?child=נעמי-מאייר          # Child slug
&hours_ahead=24            # כמה שעות קדימה לבדוק (ברירת מחדל: 24)
```

#### דוגמה:

```bash
GET https://baby.davidvmayer.com/api/webhooks/medications/
```

#### מה לעדכן ב-n8n:

1. ✅ **אין צורך לעדכן**

---

## 📊 טבלת השוואה מהירה

| Workflow      | URL ישן                        | URL חדש                    | צריך עדכון? | שינויים עיקריים                   |
| ------------- | ------------------------------ | -------------------------- | ----------- | --------------------------------- |
| Daily Summary | `/api/webhooks/daily-summary/` | ✅ זהה                     | לא (מומלץ)  | ברירת מחדל: אתמול, LLM messages   |
| Alerts        | `/api/webhooks/smart-alerts/`  | ⚠️ `/api/webhooks/alerts/` | **כן**      | מאוחד, LLM messages, Hebrew times |
| Status        | `/api/webhooks/status/`        | ✅ זהה                     | לא          | פורמט זמנים בעברית                |
| Medications   | `/api/webhooks/medications/`   | ✅ זהה                     | לא          | ללא שינוי                         |

---

## 🎨 דוגמאות להודעות החדשות

### דוגמה להתראת רעב (LLM):

```
🍼 *נעמי רעבה מאוד!*
עברו כבר _25 דקות_ מאז האכלה אחרונה 😋

זמן לבקבוק! 🍼
```

### דוגמה לסיכום יומי (LLM):

```
📊 *סיכום יום של נעמי*
יום מקסים! הרבה אכילה, שינה טובה 💕

🍼 _7 האכלות_ | 120 דקות | 850 ml
💤 _5 תקופות שינה_ | 11.5 שעות (3 תנומות)
🧷 _6 חיתולים_

ממשיכים חזק! 💪✨
```

---

## 🔧 בדיקה ואימות

### בדוק שה-webhooks עובדים:

```bash
# בדיקת alerts
curl "https://baby.davidvmayer.com/api/webhooks/alerts/" -H "Authorization: Token YOUR_TOKEN"

# בדיקת daily summary
curl "https://baby.davidvmayer.com/api/webhooks/daily-summary/" -H "Authorization: Token YOUR_TOKEN"
```

### תוצאה מצופה:

- הודעות בעברית עם markdown של WhatsApp
- זמנים בפורמט עברי קריא
- אימוג'ים והדגשות

---

## ❓ שאלות נפוצות

### Q: האם צריך API key ל-Anthropic?

**A**: לא חובה! אם אין `ANTHROPIC_API_KEY` ב-.env, המערכת תשתמש בהודעות fallback (עדיין יפות ומעוצבות).

### Q: מה אם אני רוצה את הנתונים של היום ב-daily-summary?

**A**: הוסף פרמטר: `?date={{ $today.format('YYYY-MM-DD') }}`

### Q: איך אני מכבה LLM messages?

**A**: הוסף פרמטר: `?use_llm=false`

### Q: מה קורה ל-smart-alerts הישן?

**A**: הוא נמחק. השתמש ב-`/api/webhooks/alerts/` עם כל אותם פרמטרים.

---

## 📝 Checklist לעדכון

- [ ] עדכן URL של alerts מ-`smart-alerts` ל-`alerts`
- [ ] בדוק שכל הפרמטרים עובדים
- [ ] בדוק שההודעות מגיעות ל-WhatsApp בפורמט נכון
- [ ] (אופציונלי) הוסף `ANTHROPIC_API_KEY` ל-.env לקבלת הודעות מגוונות
- [ ] בדוק את ה-quiet hours ו-snooze
- [ ] וודא ש-daily-summary מראה את אתמול

---

**עודכן**: {{ $now.format('YYYY-MM-DD') }}
**גרסה**: 2.0 - LLM Integration & Hebrew Time Formatting
