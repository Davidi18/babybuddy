# 📱 Baby Buddy + n8n + Green API - תרחישים מוכנים
# WhatsApp Automation Setup Guide

מדריך מלא עם תרחישים מוכנים לשילוב Baby Buddy עם WhatsApp דרך Green API ו-n8n.

---

## 🎯 מה נבנה

3 תרחישי אוטומציה מוכנים:
1. **סיכום יומי** - כל בוקר ב-8:00
2. **התראות חכמות** - רק כשהתינוק רעב/עייף
3. **מצב נוכחי לפי דרישה** - שלח "סטטוס" וקבל מצב

---

## 📋 דרישות מוקדמות

### 1. Baby Buddy API Token
```bash
# התחבר לשרת Baby Buddy
python manage.py drf_create_token admin

# שמור את ה-Token שמתקבל:
# Token: abc123def456...
```

### 2. Green API Account
1. הירשם ב-https://green-api.com/
2. צור Instance חדש
3. שמור:
   - **Instance ID**: `1101234567`
   - **API Token**: `abc123def456...`

### 3. n8n
- התקן n8n (cloud או self-hosted)
- או השתמש ב-n8n.cloud

---

## 🚀 תרחיש 1: סיכום יומי בוואטסאפ

### מה זה עושה:
כל בוקר ב-8:00 תקבל הודעת WhatsApp עם:
- כמה האכלות אתמול
- כמה שעות שינה
- ממוצעים שבועיים
- חיזוי להיום

### Workflow Setup:

#### Node 1: Schedule Trigger
```json
{
  "rule": "0 8 * * *",
  "triggerTimes": {
    "mode": "everyDay",
    "hour": 8,
    "minute": 0
  }
}
```

#### Node 2: HTTP Request - Baby Buddy
```json
{
  "method": "GET",
  "url": "https://your-baby-buddy.com/api/webhooks/daily-summary/",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpHeaderAuth",
  "httpHeaderAuth": {
    "name": "Authorization",
    "value": "Token YOUR_BABY_BUDDY_TOKEN"
  },
  "queryParameters": {
    "parameters": [
      {
        "name": "child",
        "value": "emma"
      }
    ]
  },
  "options": {}
}
```

#### Node 3: Green API - Send Message
```json
{
  "resource": "message",
  "operation": "sendMessage",
  "instanceId": "YOUR_INSTANCE_ID",
  "token": "YOUR_GREEN_API_TOKEN",
  "chatId": "972501234567@c.us",
  "message": "={{ $json.message }}"
}
```

**או עם HTTP Request ישירות:**
```json
{
  "method": "POST",
  "url": "https://api.green-api.com/waInstance{{YOUR_INSTANCE_ID}}/sendMessage/{{YOUR_TOKEN}}",
  "bodyParameters": {
    "parameters": [
      {
        "name": "chatId",
        "value": "972501234567@c.us"
      },
      {
        "name": "message",
        "value": "={{ $json.message }}"
      }
    ]
  }
}
```

### 📱 דוגמת הודעה שתתקבל:
```
📊 סיכום יומי - Emma
📅 25/10/2025

🍼 האכלות אתמול:
  • 8 האכלות
  • 185 דקות
  • 950 ml

💤 שינה אתמול:
  • 5 תקופות שינה
  • 12.5 שעות
  • 3 תנומות

🧷 חיתולים אתמול:
  • 9 חיתולים

📈 ממוצעים שבועיים:
  • האכלה כל 180 דקות
  • 13.2 שעות שינה ביום

🔮 חיזויים להיום:
  • האכלה הבאה: בעוד ~2 שעות
  • שינה: בעוד ~30 דקות
```

---

## ⚠️ תרחיש 2: התראות חכמות (רק כשדחוף!)

### מה זה עושה:
בודק כל 15 דקות אם יש התראה דחופה.
**שולח הודעה רק אם:**
- התינוק רעב (עבר זמן האכלה)
- התינוק עייף מדי (ער יותר מדי זמן)

### Workflow Setup:

#### Node 1: Schedule Trigger
```json
{
  "rule": "*/15 * * * *",
  "triggerTimes": {
    "mode": "everyX",
    "value": 15,
    "unit": "minutes"
  }
}
```

#### Node 2: HTTP Request - Check Alerts
```json
{
  "method": "GET",
  "url": "https://your-baby-buddy.com/api/webhooks/alerts/",
  "authentication": "genericCredentialType",
  "httpHeaderAuth": {
    "name": "Authorization",
    "value": "Token YOUR_BABY_BUDDY_TOKEN"
  },
  "queryParameters": {
    "parameters": [
      {
        "name": "child",
        "value": "emma"
      }
    ]
  }
}
```

#### Node 3: IF - יש התראות?
```json
{
  "conditions": {
    "boolean": [
      {
        "value1": "={{ $json.has_alerts }}",
        "value2": true
      }
    ]
  }
}
```

#### Node 4: Switch - סוג ההתראה (מענף True)
```json
{
  "mode": "rules",
  "rules": {
    "rules": [
      {
        "name": "רעב",
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.alerts[0].type }}",
              "operation": "equals",
              "value2": "feeding_overdue"
            }
          ]
        },
        "output": 0
      },
      {
        "name": "עייף",
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.alerts[0].type }}",
              "operation": "equals",
              "value2": "overtired"
            }
          ]
        },
        "output": 1
      }
    ]
  }
}
```

#### Node 5a: Green API - התראת רעב (Output 0)
```json
{
  "method": "POST",
  "url": "https://api.green-api.com/waInstance{{INSTANCE_ID}}/sendMessage/{{TOKEN}}",
  "body": {
    "chatId": "972501234567@c.us",
    "message": "🍼 התראה!\n\n{{ $json.alerts[0].message }}\n\nהתינוק כנראה רעב!"
  }
}
```

#### Node 5b: Green API - התראת עייפות (Output 1)
```json
{
  "method": "POST",
  "url": "https://api.green-api.com/waInstance{{INSTANCE_ID}}/sendMessage/{{TOKEN}}",
  "body": {
    "chatId": "972501234567@c.us",
    "message": "😴 התראה!\n\n{{ $json.alerts[0].message }}\n\nהתינוק עייף מדי!"
  }
}
```

### 📱 דוגמאות הודעות:
```
🍼 התראה!

עבר הזמן! התינוק כנראה רעב
(איחור של 25 דקות)

התינוק כנראה רעב!
```

```
😴 התראה!

התינוק ער כבר 2.5 שעות
(מעבר לזמן ערות טיפוסי)

התינוק עייף מדי!
```

---

## 💬 תרחיש 3: מצב נוכחי לפי דרישה

### מה זה עושה:
שלח "סטטוס" או "מצב" בWhatsApp → קבל מצב נוכחי מיידי

### Workflow Setup:

#### Node 1: Webhook Trigger (Green API)
```json
{
  "httpMethod": "POST",
  "path": "baby-status",
  "responseMode": "lastNode"
}
```

**או Green API Webhook Node:**
- Event: `incomingMessageReceived`
- Instance ID: `YOUR_INSTANCE_ID`
- Token: `YOUR_TOKEN`

#### Node 2: IF - בדוק אם זו הפקודה הנכונה
```json
{
  "conditions": {
    "string": [
      {
        "value1": "={{ $json.messageData.textMessageData.textMessage.toLowerCase() }}",
        "operation": "contains",
        "value2": "סטטוס"
      }
    ]
  }
}
```

או:
```json
{
  "conditions": {
    "string": [
      {
        "value1": "={{ $json.body.messageData.textMessageData.textMessage }}",
        "operation": "regex",
        "value2": "/(סטטוס|מצב|status)/i"
      }
    ]
  }
}
```

#### Node 3: HTTP Request - Baby Buddy (מענף True)
```json
{
  "method": "GET",
  "url": "https://your-baby-buddy.com/api/webhooks/status/",
  "authentication": "genericCredentialType",
  "httpHeaderAuth": {
    "name": "Authorization",
    "value": "Token YOUR_BABY_BUDDY_TOKEN"
  },
  "queryParameters": {
    "parameters": [
      {
        "name": "child",
        "value": "emma"
      }
    ]
  }
}
```

#### Node 4: Green API - Send Reply
```json
{
  "method": "POST",
  "url": "https://api.green-api.com/waInstance{{INSTANCE_ID}}/sendMessage/{{TOKEN}}",
  "body": {
    "chatId": "={{ $json.messageData.chatId }}",
    "message": "📊 מצב נוכחי:\n\n{{ $json.status_text }}\n\n{{ $json.next_feeding_prediction.message }}"
  }
}
```

### 📱 דוגמת שיחה:
```
אתה: סטטוס

Bot: 📊 מצב נוכחי:

👶 Emma | 🍼 האכלה: לפני 2:15

⏰ האכלה הבאה: בקרוב! בעוד ~15 דקות

💤 ער: 1:30 שעות
```

---

## 🔧 הגדרות Green API

### 1. הגדר Webhook ב-Green API
```
Settings → Webhooks
Enable: incomingMessageReceived
Webhook URL: https://your-n8n.com/webhook/baby-status
```

### 2. פורמט מספר טלפון
```
ישראל: 972501234567@c.us
ארה"ב: 1234567890@c.us
קבוצה: 120363XXXXXXXX@g.us
```

### 3. בדיקה
```bash
# שלח הודעת בדיקה
curl -X POST \
  "https://api.green-api.com/waInstance{{INSTANCE_ID}}/sendMessage/{{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "chatId": "972501234567@c.us",
    "message": "בדיקה!"
  }'
```

---

## 📦 ייבוא Workflows מוכנים

### JSON Exports (להעתיק ל-n8n)

**איך להשתמש:**
1. העתק את ה-JSON המלא
2. ב-n8n: לחץ על "+" → "Import from File/URL"
3. הדבק את ה-JSON
4. עדכן את ה-Credentials (URLs, Tokens)
5. Activate!

---

#### Workflow 1: Daily Summary
```json
{
  "name": "Baby Buddy - Daily Summary",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 8 * * *"
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://your-baby-buddy.com/api/webhooks/daily-summary/?child=emma",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "httpHeaderAuth": "={{$credentials.babyBuddyToken}}"
      },
      "name": "Get Daily Summary",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    },
    {
      "parameters": {
        "method": "POST",
        "url": "https://api.green-api.com/waInstance{{$credentials.greenApiInstanceId}}/sendMessage/{{$credentials.greenApiToken}}",
        "bodyParameters": {
          "parameters": [
            {
              "name": "chatId",
              "value": "={{$credentials.whatsappNumber}}"
            },
            {
              "name": "message",
              "value": "={{$json.message}}"
            }
          ]
        }
      },
      "name": "Send WhatsApp",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 300]
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [[{"node": "Get Daily Summary", "type": "main", "index": 0}]]
    },
    "Get Daily Summary": {
      "main": [[{"node": "Send WhatsApp", "type": "main", "index": 0}]]
    }
  }
}
```

---

#### Workflow 2: Smart Alerts (התראות חכמות)
```json
{
  "name": "Baby Buddy - Smart Alerts",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "*/15 * * * *"
            }
          ]
        }
      },
      "name": "Every 15 Minutes",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300],
      "id": "node-1"
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://your-baby-buddy.com/api/webhooks/alerts/?child=emma",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "httpHeaderAuth": "babyBuddyToken"
      },
      "name": "Check Alerts",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "id": "node-2"
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{$json.has_alerts}}",
              "value2": true
            }
          ]
        }
      },
      "name": "Has Alerts?",
      "type": "n8n-nodes-base.if",
      "position": [650, 300],
      "id": "node-3"
    },
    {
      "parameters": {
        "mode": "rules",
        "rules": {
          "rules": [
            {
              "name": "Feeding Overdue",
              "conditions": {
                "string": [
                  {
                    "value1": "={{$json.alerts[0].type}}",
                    "operation": "equals",
                    "value2": "feeding_overdue"
                  }
                ]
              },
              "renameOutput": true,
              "outputKey": "feeding"
            },
            {
              "name": "Overtired",
              "conditions": {
                "string": [
                  {
                    "value1": "={{$json.alerts[0].type}}",
                    "operation": "equals",
                    "value2": "overtired"
                  }
                ]
              },
              "renameOutput": true,
              "outputKey": "sleep"
            }
          ]
        }
      },
      "name": "Alert Type",
      "type": "n8n-nodes-base.switch",
      "position": [850, 200],
      "id": "node-4"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "=https://api.green-api.com/waInstance{{$credentials.greenApiInstanceId}}/sendMessage/{{$credentials.greenApiToken}}",
        "bodyParameters": {
          "parameters": [
            {
              "name": "chatId",
              "value": "={{$credentials.whatsappNumber}}"
            },
            {
              "name": "message",
              "value": "=🍼 התראה!\n\n{{$json.alerts[0].message}}\n\nהתינוק כנראה רעב!"
            }
          ]
        },
        "options": {}
      },
      "name": "Send Feeding Alert",
      "type": "n8n-nodes-base.httpRequest",
      "position": [1050, 100],
      "id": "node-5"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "=https://api.green-api.com/waInstance{{$credentials.greenApiInstanceId}}/sendMessage/{{$credentials.greenApiToken}}",
        "bodyParameters": {
          "parameters": [
            {
              "name": "chatId",
              "value": "={{$credentials.whatsappNumber}}"
            },
            {
              "name": "message",
              "value": "=😴 התראה!\n\n{{$json.alerts[0].message}}\n\nהתינוק עייף מדי!"
            }
          ]
        },
        "options": {}
      },
      "name": "Send Sleep Alert",
      "type": "n8n-nodes-base.httpRequest",
      "position": [1050, 300],
      "id": "node-6"
    }
  ],
  "connections": {
    "Every 15 Minutes": {
      "main": [[{"node": "Check Alerts", "type": "main", "index": 0}]]
    },
    "Check Alerts": {
      "main": [[{"node": "Has Alerts?", "type": "main", "index": 0}]]
    },
    "Has Alerts?": {
      "main": [
        [{"node": "Alert Type", "type": "main", "index": 0}],
        []
      ]
    },
    "Alert Type": {
      "main": [
        [{"node": "Send Feeding Alert", "type": "main", "index": 0}],
        [{"node": "Send Sleep Alert", "type": "main", "index": 0}]
      ]
    }
  }
}
```

---

#### Workflow 3: Status On Demand (מצב לפי דרישה)
```json
{
  "name": "Baby Buddy - Status On Demand",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "baby-status",
        "responseMode": "lastNode",
        "options": {}
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "webhookId": "baby-status-webhook",
      "id": "node-1"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json.body.messageData.textMessageData.textMessage.toLowerCase()}}",
              "operation": "regex",
              "value2": "(סטטוס|מצב|status)"
            }
          ]
        }
      },
      "name": "Is Status Command?",
      "type": "n8n-nodes-base.if",
      "position": [450, 300],
      "id": "node-2"
    },
    {
      "parameters": {
        "method": "GET",
        "url": "https://your-baby-buddy.com/api/webhooks/status/?child=emma",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "httpHeaderAuth": "babyBuddyToken"
      },
      "name": "Get Status",
      "type": "n8n-nodes-base.httpRequest",
      "position": [650, 200],
      "id": "node-3"
    },
    {
      "parameters": {
        "method": "POST",
        "url": "=https://api.green-api.com/waInstance{{$credentials.greenApiInstanceId}}/sendMessage/{{$credentials.greenApiToken}}",
        "bodyParameters": {
          "parameters": [
            {
              "name": "chatId",
              "value": "={{$json.body.senderData.chatId}}"
            },
            {
              "name": "message",
              "value": "=📊 מצב נוכחי:\n\n{{$json.status_text}}\n\n{{$json.next_feeding_prediction.message}}"
            }
          ]
        }
      },
      "name": "Send Status Reply",
      "type": "n8n-nodes-base.httpRequest",
      "position": [850, 200],
      "id": "node-4"
    },
    {
      "parameters": {
        "respondWith": "text",
        "responseBody": "=OK"
      },
      "name": "Respond to Webhook",
      "type": "n8n-nodes-base.respondToWebhook",
      "position": [1050, 200],
      "id": "node-5"
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Is Status Command?", "type": "main", "index": 0}]]
    },
    "Is Status Command?": {
      "main": [
        [{"node": "Get Status", "type": "main", "index": 0}],
        []
      ]
    },
    "Get Status": {
      "main": [[{"node": "Send Status Reply", "type": "main", "index": 0}]]
    },
    "Send Status Reply": {
      "main": [[{"node": "Respond to Webhook", "type": "main", "index": 0}]]
    }
  },
  "settings": {
    "executionOrder": "v1"
  }
}
```

---

## 🎨 התאמה אישית

### שנה את זמני ההתראות
```javascript
// בNode של Schedule Trigger
// כל 10 דקות במקום 15:
"rule": "*/10 * * * *"

// כל שעה:
"rule": "0 * * * *"

// כל יום ב-7:30 בבוקר:
"rule": "30 7 * * *"
```

### הוסף אמוג'י מותאם אישית
```javascript
// בNode של Send Message
const emoji = {
  feeding_overdue: "🍼❗",
  overtired: "😴💤",
  diaper_overdue: "🧷⏰"
};

const message = `${emoji[$json.alerts[0].type]} ${$json.alerts[0].message}`;
```

### שלח לכמה אנשים
```javascript
// הוסף Node "Split In Batches"
const recipients = [
  "972501234567@c.us",  // אמא
  "972509876543@c.us",  // אבא
  "972501111111@c.us"   // סבתא
];

// בלולאה שלח לכל אחד
```

---

## 🐛 Troubleshooting

### הודעות לא מגיעות?
1. **בדוק Token:**
   ```bash
   curl "https://your-baby-buddy.com/api/webhooks/status/" \
     -H "Authorization: Token YOUR_TOKEN"
   ```

2. **בדוק Green API Instance:**
   ```bash
   curl "https://api.green-api.com/waInstance{{ID}}/getStateInstance/{{TOKEN}}"
   # צריך להחזיר: "authorized"
   ```

3. **בדוק פורמט מספר:**
   - ✅ `972501234567@c.us`
   - ❌ `+972-50-123-4567`
   - ❌ `0501234567`

### n8n לא מריץ את ה-Workflow?
1. וודא ש-Workflow מופעל (toggle בפינה)
2. בדוק Executions → Errors
3. Test Workflow ידנית

### Baby Buddy מחזיר שגיאה?
```json
// שגיאה: "Authentication credentials were not provided"
→ בדוק שה-Header נכון: "Authorization: Token XXX"

// שגיאה: "Child not found"
→ בדוק את ה-slug בURL: ?child=emma

// שגיאה: "Not enough data"
→ הוסף עוד רשומות (לפחות 3-4 ימים)
```

---

## 📊 סטטיסטיקות שימוש

### כמה API Calls?
- **סיכום יומי:** 1 call ליום = ~30/חודש
- **התראות:** 96 calls ליום (כל 15 דקות) = ~2,880/חודש
- **מצב לפי דרישה:** תלוי בך

**Green API Free Tier:** 1,000 הודעות/חודש
→ מספיק לכל התרחישים! ✅

---

## 🎓 למידע נוסף

- **Baby Buddy API:** `N8N_WEBHOOKS_GUIDE.md`
- **Green API Docs:** https://green-api.com/docs/
- **n8n Docs:** https://docs.n8n.io/

---

## ✨ רעיונות נוספים

### 🏠 Home Assistant Integration
```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: baby_last_feeding
    resource: https://baby.com/api/webhooks/status/
    headers:
      Authorization: Token YOUR_TOKEN
    value_template: "{{ value_json.last_feeding_minutes_ago }}"
```

### 📈 Google Sheets Logging
הוסף Node "Google Sheets" אחרי Baby Buddy:
- שמור כל התראה בגיליון
- צור גרפים אוטומטיים
- נתח דפוסים

### 🔔 Telegram במקום WhatsApp
החלף Green API ב-Telegram Bot:
```json
{
  "name": "Telegram",
  "type": "n8n-nodes-base.telegram",
  "parameters": {
    "chatId": "YOUR_CHAT_ID",
    "text": "={{$json.message}}"
  }
}
```

---

**🎉 מוכן! עכשיו יש לך אוטומציה מלאה של Baby Buddy בWhatsApp!**

💡 **טיפ:** התחל עם תרחיש 1 (סיכום יומי), ואז הוסף את השאר בהדרגה.
