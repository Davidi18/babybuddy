# n8n Workflow - Smart Alerts System

## קובץ workflow מלא זמין להורדה בגיטהאב

העתק את התוכן של הקובץ `n8n-workflows-ready-to-import.json` הקיים וערוך אותו.

## או השתמש בהוראות האלה:

### צור workflow חדש ב-n8n:

1. **Schedule Trigger** - כל 10 דקות
2. **HTTP Request** - Get Smart Alerts
   - URL: `https://YOUR-DOMAIN.com/api/webhooks/smart-alerts/`
   - Method: GET
   - Query Parameters:
     - child: YOUR_CHILD_SLUG
     - feeding_threshold: 20
     - sleep_threshold: 100
     - quiet_hours_start: 23
     - quiet_hours_end: 6
     - snooze_minutes: 30
   - Auth: Header Auth (Baby Buddy Token)

3. **IF Node** - Has Alerts?
   - Condition: `{{$json.has_alerts}}` = true

4. **IF Node** - Is Quiet Hours?
   - Condition: `{{$json.quiet_hours}}` = false

5. **Switch Node** - Alert Type
   - Rule 1: `{{$json.alerts[0].type}}` = "feeding_overdue"
   - Rule 2: `{{$json.alerts[0].type}}` = "overtired"  
   - Rule 3: `{{$json.alerts[0].type}}` = "diaper_overdue"

6. **HTTP Request** (3 nodes) - Send WhatsApp
   - Feeding: 🍼 message
   - Sleep: 😴 message
   - Diaper: 🧷 message

## הודעות לדוגמה:

```
🍼 *{{$json.alerts[0].title}}*

{{$json.alerts[0].message}}

_סף: {{$json.alerts[0].threshold_used}} דקות_
```

להורדה של workflow מלא, ראה בקובץ המקורי או פנה לתיעוד.
