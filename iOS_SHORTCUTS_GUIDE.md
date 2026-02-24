# Baby Buddy - iOS Shortcuts למעקב אחרי נעמי

## הפרטים שלך (מוכנים להעתקה)

| פרט | ערך |
|------|------|
| **Server URL** | `https://baby.davidvmayer.com` |
| **API Key** | `013a452982f3d41cf2a9af865c71660d62365b89` |
| **Child ID** | `1` (נעמי מאייר) |

**Header שחוזר בכל Shortcut:**
```
Authorization: Token 013a452982f3d41cf2a9af865c71660d62365b89
Content-Type: application/json
```

---

## Shortcut #1: "נעמי נרדמה" (מעקב שינה - התחלה)

**פקודת Siri:** "Hey Siri, נעמי נרדמה"

### שלבים:

1. **פתח Shortcuts** → לחץ **+** → תן שם: **"נעמי נרדמה"**

2. **הוסף Action: "Get Contents of URL"**
   - URL: `https://baby.davidvmayer.com/api/timers/`
   - Method: **POST**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`
     - `Content-Type` = `application/json`
   - Request Body: **JSON**
     - `child` = `1` (Number)
     - `name` = `Sleep` (Text)

3. **הוסף Action: "Show Notification"**
   - Title: `נעמי נרדמה`
   - Body: `טיימר שינה התחיל`

---

## Shortcut #2: "נעמי קמה" (מעקב שינה - סיום)

**פקודת Siri:** "Hey Siri, נעמי קמה"

### שלבים:

1. **פתח Shortcuts** → לחץ **+** → תן שם: **"נעמי קמה"**

2. **הוסף Action: "Get Contents of URL"** (שליפת טיימר פעיל)
   - URL: `https://baby.davidvmayer.com/api/timers/?child=1&name=Sleep`
   - Method: **GET**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`

3. **הוסף Action: "Get Dictionary Value"**
   - Key: `results`
   - Dictionary: `Contents of URL`

4. **הוסף Action: "Get Item from List"**
   - Get: **First Item**
   - List: `Dictionary Value`

5. **הוסף Action: "Get Dictionary Value"**
   - Key: `id`
   - Dictionary: `Item from List`

6. **הוסף Action: "Get Contents of URL"** (שמירת רשומת שינה)
   - URL: `https://baby.davidvmayer.com/api/sleep/`
   - Method: **POST**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`
     - `Content-Type` = `application/json`
   - Request Body: **JSON**
     - `timer` = `Dictionary Value` (Magic Variable - מהשלב הקודם)

7. **הוסף Action: "Show Notification"**
   - Title: `נעמי קמה!`
   - Body: `השינה נרשמה בהצלחה`

---

## Shortcut #3: "האכלה מהירה" (120ml)

**פקודת Siri:** "Hey Siri, האכלה מהירה"

### שלבים:

1. **פתח Shortcuts** → לחץ **+** → תן שם: **"האכלה מהירה"**

2. **הוסף Action: "Date"** (Current Date)
   - בחר: **Current Date**

3. **הוסף Action: "Format Date"**
   - Date: `Current Date`
   - Date Format: **Custom**
   - Format String: `yyyy-MM-dd'T'HH:mm:ssZ`

4. **הוסף Action: "Get Contents of URL"**
   - URL: `https://baby.davidvmayer.com/api/feedings/`
   - Method: **POST**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`
     - `Content-Type` = `application/json`
   - Request Body: **JSON**
     - `child` = `1` (Number)
     - `start` = `Formatted Date` (Magic Variable)
     - `end` = `Formatted Date` (Magic Variable)
     - `type` = `formula` (Text)
     - `method` = `bottle` (Text)
     - `amount` = `120` (Number)

5. **הוסף Action: "Show Notification"**
   - Title: `האכלה נרשמה`
   - Body: `120ml formula נרשמו לנעמי`

---

## Shortcut #4: "האכלה" (עם בחירת כמות)

**פקודת Siri:** "Hey Siri, האכלה"

### שלבים:

1. **פתח Shortcuts** → לחץ **+** → תן שם: **"האכלה"**

2. **הוסף Action: "Ask for Input"**
   - Question: `כמה ml?`
   - Input Type: **Number**
   - Default Answer: `120`

3. **הוסף Action: "Date"** → Current Date

4. **הוסף Action: "Format Date"**
   - Date Format: **Custom**
   - Format String: `yyyy-MM-dd'T'HH:mm:ssZ`

5. **הוסף Action: "Get Contents of URL"**
   - URL: `https://baby.davidvmayer.com/api/feedings/`
   - Method: **POST**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`
     - `Content-Type` = `application/json`
   - Request Body: **JSON**
     - `child` = `1` (Number)
     - `start` = `Formatted Date` (Magic Variable)
     - `end` = `Formatted Date` (Magic Variable)
     - `type` = `formula` (Text)
     - `method` = `bottle` (Text)
     - `amount` = `Provided Input` (Magic Variable)

6. **הוסף Action: "Show Notification"**
   - Title: `האכלה נרשמה`
   - Body: `Provided Input` + `ml נרשמו לנעמי`

---

## Shortcut #5: "החלפת חיתול"

**פקודת Siri:** "Hey Siri, החלפת חיתול"

### שלבים:

1. **פתח Shortcuts** → לחץ **+** → תן שם: **"החלפת חיתול"**

2. **הוסף Action: "Choose from Menu"**
   - Prompt: `איזה סוג?`
   - Options: `רטוב`, `מוצק`, `שניהם`

3. **תחת "רטוב" - הוסף "Get Contents of URL":**
   - URL: `https://baby.davidvmayer.com/api/changes/`
   - Method: **POST**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`
     - `Content-Type` = `application/json`
   - Request Body: **JSON**
     - `child` = `1` (Number)
     - `time` = `Current Date` (Magic Variable)
     - `wet` = `true` (Boolean)
     - `solid` = `false` (Boolean)

4. **תחת "מוצק" - הוסף "Get Contents of URL":**
   - אותו דבר, רק:
     - `wet` = `false` (Boolean)
     - `solid` = `true` (Boolean)

5. **תחת "שניהם" - הוסף "Get Contents of URL":**
   - אותו דבר, רק:
     - `wet` = `true` (Boolean)
     - `solid` = `true` (Boolean)

6. **אחרי ה-Menu - הוסף Action: "Show Notification"**
   - Title: `חיתול הוחלף`
   - Body: `נרשם לנעמי`

---

## Shortcut #6: "התחל זמן בטן" (Tummy Time - התחלה)

**פקודת Siri:** "Hey Siri, זמן בטן"

### שלבים:

1. **פתח Shortcuts** → לחץ **+** → תן שם: **"זמן בטן"**

2. **הוסף Action: "Get Contents of URL"**
   - URL: `https://baby.davidvmayer.com/api/timers/`
   - Method: **POST**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`
     - `Content-Type` = `application/json`
   - Request Body: **JSON**
     - `child` = `1` (Number)
     - `name` = `Tummy Time` (Text)

3. **הוסף Action: "Show Notification"**
   - Title: `זמן בטן התחיל!`
   - Body: `טיימר רץ לנעמי`

---

## Shortcut #7: "סיים זמן בטן" (Tummy Time - סיום)

**פקודת Siri:** "Hey Siri, סיים זמן בטן"

### שלבים:

1. **פתח Shortcuts** → לחץ **+** → תן שם: **"סיים זמן בטן"**

2. **הוסף Action: "Get Contents of URL"** (שליפת טיימר)
   - URL: `https://baby.davidvmayer.com/api/timers/?child=1&name=Tummy+Time`
   - Method: **GET**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`

3. **הוסף Action: "Get Dictionary Value"**
   - Key: `results`
   - Dictionary: `Contents of URL`

4. **הוסף Action: "Get Item from List"**
   - Get: **First Item**

5. **הוסף Action: "Get Dictionary Value"**
   - Key: `id`
   - Dictionary: `Item from List`

6. **הוסף Action: "Get Contents of URL"** (שמירת זמן בטן)
   - URL: `https://baby.davidvmayer.com/api/tummy-times/`
   - Method: **POST**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`
     - `Content-Type` = `application/json`
   - Request Body: **JSON**
     - `timer` = `Dictionary Value` (Magic Variable)

7. **הוסף Action: "Show Notification"**
   - Title: `זמן בטן הסתיים!`
   - Body: `נרשם לנעמי`

---

## Shortcut #8: "סיכום יום"

**פקודת Siri:** "Hey Siri, סיכום יום נעמי"

### שלבים:

1. **פתח Shortcuts** → לחץ **+** → תן שם: **"סיכום יום נעמי"**

2. **הוסף Action: "Date"** → Current Date

3. **הוסף Action: "Format Date"**
   - Date Format: **Custom**
   - Format String: `yyyy-MM-dd`

4. **הוסף Action: "Get Contents of URL"** (האכלות)
   - URL: `https://baby.davidvmayer.com/api/feedings/?child=1&start_min=` + `Formatted Date`
   - Method: **GET**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`

5. **הוסף Action: "Get Dictionary Value"**
   - Key: `count`
   - Dictionary: `Contents of URL`

6. **הוסף Action: "Set Variable"**
   - Variable Name: `FeedingsCount`

7. **הוסף Action: "Get Contents of URL"** (חיתולים)
   - URL: `https://baby.davidvmayer.com/api/changes/?child=1&date_min=` + `Formatted Date`
   - Method: **GET**
   - Headers:
     - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`

8. **הוסף Action: "Get Dictionary Value"**
   - Key: `count`

9. **הוסף Action: "Set Variable"**
   - Variable Name: `ChangesCount`

10. **הוסף Action: "Get Contents of URL"** (שינה)
    - URL: `https://baby.davidvmayer.com/api/sleep/?child=1&start_min=` + `Formatted Date`
    - Method: **GET**
    - Headers:
      - `Authorization` = `Token 013a452982f3d41cf2a9af865c71660d62365b89`

11. **הוסף Action: "Get Dictionary Value"**
    - Key: `count`

12. **הוסף Action: "Set Variable"**
    - Variable Name: `SleepCount`

13. **הוסף Action: "Show Result"**
    ```
    סיכום יומי - נעמי:
    האכלות: FeedingsCount
    החלפות חיתול: ChangesCount
    שינות: SleepCount
    ```

---

## טיפים

### Widget על מסך הבית
1. לחץ לחוץ על מסך הבית → **+** (למעלה שמאל)
2. חפש **Shortcuts**
3. בחר widget בגודל שמתאים
4. הוסף את הקיצורים הכי שימושיים

### Back Tap (הקשה על גב האייפון)
1. Settings → Accessibility → Touch → Back Tap
2. Double Tap → בחר Shortcut (למשל "החלפת חיתול")
3. עכשיו הקשה כפולה על גב האייפון = רישום!

### Siri - כל הפקודות:
- "Hey Siri, נעמי נרדמה"
- "Hey Siri, נעמי קמה"
- "Hey Siri, האכלה מהירה"
- "Hey Siri, האכלה"
- "Hey Siri, החלפת חיתול"
- "Hey Siri, זמן בטן"
- "Hey Siri, סיים זמן בטן"
- "Hey Siri, סיכום יום נעמי"

---

## פתרון בעיות

### "403 Forbidden"
- ודא שיש **רווח** אחרי "Token" ב-Header
- נכון: `Token 013a452982f3d41cf2a9af865c71660d62365b89`
- לא נכון: `Token013a452982f3d41cf2a9af865c71660d62365b89`

### "Current Date לא עובד בפורמט"
- השתמש ב-"Format Date" Action עם פורמט: `yyyy-MM-dd'T'HH:mm:ssZ`

### "הטיימר לא נמצא ב-'נעמי קמה'"
- ודא שהפעלת את "נעמי נרדמה" קודם
- אם הטיימר נמחק בטעות, צור רשומת שינה ידנית דרך האתר

### "SSL Error" / "Certificate Error"
- ודא שהכתובת מתחילה ב-`https://`
- אם יש בעיית תעודה, נסה את הכתובת בדפדפן קודם
