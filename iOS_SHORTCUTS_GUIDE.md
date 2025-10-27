# 📱 Baby Buddy - iOS Shortcuts + Smart Timers

## 🎯 מערכת טיימרים חכמה חדשה!

Baby Buddy עכשיו כולל מערכת טיימרים חכמה עם תבניות מוכנות:

### ✨ תבניות טיימר מהירות:

- 😴 **Sleep Timer** - התחל מיד, סיים והמר לשינה
- 🤸 **Tummy Time Timer** - התחל מיד, סיים והמר לזמן בטן
- 🍼 **Pumping Timer** - התחל מיד, סיים והמר לשאיבה

### 🚀 איך להשתמש:

1. לחץ על **Timers** בתפריט
2. בחר תבנית (למשל: "Feeding Timer")
3. הטיימר מתחיל לרוץ מיד!
4. כשגמרת - לחץ **Stop & Save**
5. הטופס נפתח אוטומטית עם הזמנים מהטיימר
6. השלם פרטים נוספים (כמות, סוג, וכו') ושמור!

---

## מה זה iOS Shortcuts?

אפליקציית Shortcuts של אפל מאפשרת לך ליצור "קיצורים" שמבצעים פעולות אוטומטיות.
במקרה שלנו - לרשום פעילויות ב-Baby Buddy בלחיצה אחת או פקודת Siri.

---

## 🚀 התחלה מהירה (5 דקות)

### שלב 1: קבל את ה-API Key שלך

1. פתח http://127.0.0.1:8000 בדפדפן
2. התחבר (admin/admin)
3. לך ל-**User Settings**
4. העתק את ה-**API Key**

### שלב 2: פתח את אפליקציית Shortcuts באייפון

- אפליקציה כחולה עם סמל של שני ריבועים

### שלב 3: צור Shortcut ראשון

נתחיל עם משהו פשוט - רישום האכלה של 120ml

---

## 📝 Shortcut #1: רישום האכלה מהירה

### מה זה עושה:

לחיצה אחת → רושם האכלה של 120ml

### איך לבנות:

1. **פתח Shortcuts** → לחץ על **+** (למעלה מימין)

2. **הוסף Action** → חפש **"Get Contents of URL"**

3. **הגדר את הבקשה:**

   ```
   URL: http://YOUR_IP:8000/api/feedings/
   Method: POST
   Headers:
     Authorization: Token YOUR_API_KEY_HERE
     Content-Type: application/json
   Request Body: JSON
   ```

4. **הוסף JSON Body** (לחץ על "Request Body"):

   ```json
   {
     "child": 1,
     "start": "{{Current Date}}",
     "end": "{{Current Date}}",
     "type": "bottle",
     "method": "bottle",
     "amount": 120
   }
   ```

5. **הוסף התראה** → חפש **"Show Notification"**

   ```
   Title: ✅ האכלה נרשמה
   Body: 120ml נרשמו בהצלחה
   ```

6. **שמור** → תן שם: "האכלה 120ml"

### איך להשתמש:

- **מהאפליקציה**: פתח Shortcuts → לחץ על "האכלה 120ml"
- **מ-Widget**: הוסף Shortcuts widget למסך הבית
- **עם Siri**: "Hey Siri, האכלה 120ml"

---

## 📝 Shortcut #2: רישום האכלה עם כמות משתנה

### מה זה עושה:

שואל כמה ml → רושם את הכמות

### איך לבנות:

1. **צור Shortcut חדש**

2. **הוסף "Ask for Input"**

   ```
   Question: כמה ml?
   Input Type: Number
   Default: 120
   ```

3. **הוסף "Get Contents of URL"**

   ```
   URL: http://YOUR_IP:8000/api/feedings/
   Method: POST
   Headers:
     Authorization: Token YOUR_API_KEY_HERE
     Content-Type: application/json
   ```

4. **JSON Body:**

   ```json
   {
     "child": 1,
     "start": "{{Current Date}}",
     "end": "{{Current Date}}",
     "type": "bottle",
     "method": "bottle",
     "amount": {{Provided Input}}
   }
   ```

5. **הוסף התראה**
   ```
   Title: ✅ האכלה נרשמה
   Body: {{Provided Input}}ml נרשמו
   ```

---

## 📝 Shortcut #3: התחל טיימר האכלה (מתקדם!)

### 🎯 מה זה עושה:

מתחיל טיימר של iOS → בסוף מתחבר ל-Baby Buddy ורושם אוטומטית!

### 🚀 איך לבנות:

**חלק א' - התחל טיימר עם Baby Buddy:**

1. **צור Shortcut חדש** → שם: "התחל האכלה"

2. **הוסף "Start Timer"** (טיימר של iOS)

   ```
   Label: האכלה
   ```

3. **הוסף "Get Contents of URL"** (אופציונלי - התחל גם טיימר ב-Baby Buddy)

   ```
   URL: http://YOUR_IP:8000/timers/quick/feeding/
   Method: GET
   Headers:
     Cookie: sessionid=YOUR_SESSION_ID
   ```

4. **הוסף התראה**
   ```
   Title: 🍼 טיימר האכלה התחיל!
   Body: לחץ "סיים האכלה" כשגמרת
   ```

**חלק ב' - סיים טיימר:**

1. **צור Shortcut חדש** → שם: "סיים האכלה"

2. **הוסף "Get Latest Timer"** (מטיימר של iOS)

3. **הוסף "Calculate" → Duration**

   ```
   Get duration of Timer
   Convert to Minutes
   ```

4. **הוסף "Ask for Input"**

   ```
   Question: כמה ml?
   Input Type: Number
   Default: 120
   ```

5. **הוסף "Get Contents of URL"**

   ```
   URL: http://YOUR_IP:8000/api/timers/
   Method: POST
   Headers:
     Authorization: Token YOUR_API_KEY_HERE
     Content-Type: application/json
   ```

6. **JSON Body:**

   ```json
   {
     "child": 1,
     "name": "Feeding"
   }
   ```

7. **הוסף "Get Dictionary Value"**

   - Key: `id`
   - Dictionary: `Contents of URL`

8. **הוסף "Set Variable"**

   - Variable Name: `TimerID`
   - Value: `Dictionary Value`

9. **הוסף "Show Notification"**
   ```
   Title: ⏱ טיימר התחיל
   Body: לחץ על "סיים האכלה" כשגמרת
   ```

**חלק ב' - סיים טיימר:**

1. **צור Shortcut חדש** → שם: "סיים האכלה"

2. **הוסף "Ask for Input"**

   ```
   Question: כמה ml?
   Input Type: Number
   ```

3. **הוסף "Get Contents of URL"** (לקבל את הטיימר הפעיל)

   ```
   URL: http://YOUR_IP:8000/api/timers/
   Method: GET
   Headers:
     Authorization: Token YOUR_API_KEY_HERE
   ```

4. **הוסף "Get Dictionary Value"**

   - Key: `results`
   - Dictionary: `Contents of URL`

5. **הוסף "Get Item from List"**

   - Get: `First Item`
   - List: `Dictionary Value`

6. **הוסף "Get Dictionary Value"**

   - Key: `id`
   - Dictionary: `Item from List`

7. **הוסף "Get Contents of URL"** (סיים את הטיימר)

   ```
   URL: http://YOUR_IP:8000/api/feedings/
   Method: POST
   Headers:
     Authorization: Token YOUR_API_KEY_HERE
     Content-Type: application/json
   ```

8. **JSON Body:**

   ```json
   {
     "timer": {{Dictionary Value}},
     "type": "bottle",
     "method": "bottle",
     "amount": {{Provided Input}}
   }
   ```

9. **הוסף התראה**
   ```
   Title: ✅ האכלה הושלמה
   Body: {{Provided Input}}ml נרשמו
   ```

---

## 📝 Shortcut #4: רישום החלפת חיתול

### מה זה עושה:

שואל רטוב/מוצק → רושם החלפה

### איך לבנות:

1. **צור Shortcut חדש** → שם: "החלפת חיתול"

2. **הוסף "Choose from Menu"**

   ```
   Prompt: איזה סוג?
   Options:
     - רטוב
     - מוצק
     - שניהם
   ```

3. **תחת "רטוב":**

   - **הוסף "Get Contents of URL"**
     ```
     URL: http://YOUR_IP:8000/api/changes/
     Method: POST
     Headers:
       Authorization: Token YOUR_API_KEY_HERE
       Content-Type: application/json
     ```
   - **JSON Body:**
     ```json
     {
       "child": 1,
       "time": "{{Current Date}}",
       "wet": true,
       "solid": false
     }
     ```

4. **תחת "מוצק":**

   - אותו דבר אבל:
     ```json
     {
       "child": 1,
       "time": "{{Current Date}}",
       "wet": false,
       "solid": true
     }
     ```

5. **תחת "שניהם":**

   - אותו דבר אבל:
     ```json
     {
       "child": 1,
       "time": "{{Current Date}}",
       "wet": true,
       "solid": true
     }
     ```

6. **הוסף התראה בסוף**
   ```
   Title: ✅ החלפה נרשמה
   ```

---

## 📝 Shortcut #5: סיכום יומי

### מה זה עושה:

מציג כמה האכלות/החלפות היו היום

### איך לבנות:

1. **צור Shortcut חדש** → שם: "סיכום יום"

2. **הוסף "Get Current Date"**

3. **הוסף "Format Date"**

   - Date: `Current Date`
   - Format: `Custom`
   - Format String: `yyyy-MM-dd`

4. **הוסף "Get Contents of URL"** (האכלות)

   ```
   URL: http://YOUR_IP:8000/api/feedings/?child=1&start__gte={{Formatted Date}}
   Method: GET
   Headers:
     Authorization: Token YOUR_API_KEY_HERE
   ```

5. **הוסף "Get Dictionary Value"**

   - Key: `count`
   - Dictionary: `Contents of URL`

6. **הוסף "Set Variable"**

   - Variable Name: `FeedingsCount`

7. **חזור על שלבים 4-6 ל-`/api/changes/`** (החלפות)

8. **הוסף "Show Result"**
   ```
   📊 סיכום יומי:
   🍼 האכלות: {{FeedingsCount}}
   🚼 החלפות: {{ChangesCount}}
   ```

---

## 🎯 טיפים מעשיים

### 1. **Widget על מסך הבית**

- הוסף Shortcuts widget
- בחר את הקיצורים הכי נפוצים
- גישה מהירה בלי לפתוח אפליקציה

### 2. **Back Tap (הקשה כפולה על גב האייפון)**

- הגדרות → Accessibility → Touch → Back Tap
- Double Tap → בחר Shortcut
- עכשיו הקשה כפולה על גב האייפון = רישום האכלה!

### 3. **Siri**

- כל Shortcut אפשר להפעיל עם Siri
- "Hey Siri, האכלה 120ml"
- "Hey Siri, החלפת חיתול"
- "Hey Siri, סיכום יום"

### 4. **Automation (אוטומציה)**

- Shortcuts → Automation → Create Personal Automation
- דוגמאות:
  - כל יום ב-20:00 → שלח סיכום יומי
  - כשמגיע הביתה → שאל אם צריך לרשום משהו
  - כשמתחבר ל-CarPlay → הצג תזכורת

### 5. **Share Sheet**

- הפעל Shortcut מכל אפליקציה
- שתף → בחר Shortcut
- שימושי פחות אבל אפשרי

---

## 🔧 פתרון בעיות

### "לא מצליח להתחבר"

- ✅ בדוק שהאייפון והמחשב באותה רשת WiFi
- ✅ השתמש בכתובת IP של המחשב (לא localhost)
- ✅ מצא IP: `ifconfig | grep inet` (Mac) או הגדרות רשת (Windows)

### "403 Forbidden"

- ✅ בדוק את ה-API Key
- ✅ ודא שיש רווח אחרי "Token" בheader
- ✅ נכון: `Token abc123`
- ✅ לא נכון: `Tokenabc123`

### "השרת לא עונה"

- ✅ בדוק שהשרת רץ: `ps aux | grep runserver`
- ✅ נסה לפתוח בדפדפן באייפון: `http://YOUR_IP:8000`

### "Current Date לא עובד"

- ✅ השתמש ב-"Current Date" מהרשימה (לא כתוב ידנית)
- ✅ Format: ISO 8601 (`yyyy-MM-dd'T'HH:mm:ssZ`)

---

## 📦 Shortcuts מוכנים להורדה

אם יש לך קישור ל-iCloud, אפשר לשתף Shortcuts.
אבל בגלל שכל אחד צריך API Key משלו, עדיף לבנות בעצמך (5 דקות).

---

## 💡 רעיונות נוספים (פשוטים)

### Shortcut מהיר לכל כמות

צור 3 shortcuts:

- "האכלה 90" → 90ml
- "האכלה 120" → 120ml
- "האכלה 150" → 150ml

שים אותם ב-widget, ובלחיצה אחת זה נרשם.

### Shortcut עם תזכורת

אחרי שרושם האכלה, הוסף:

- "Wait" → 3 hours
- "Show Notification" → "זמן להאכיל!"

### Shortcut לשיתוף עם בן/בת זוג

אחרי רישום, שלח הודעה:

- "Send Message" → לבן/בת זוג
- "התינוק אכל 120ml ב-{{Current Time}}"

---

## 🎉 סיכום

**מה צריך:**

1. ✅ Baby Buddy רץ על המחשב
2. ✅ אייפון ומחשב באותה רשת
3. ✅ API Key
4. ✅ 5 דקות לבנות Shortcut

**מה מקבלים:**

- 🍼 רישום האכלה בלחיצה אחת
- 🚼 רישום החלפה בלחיצה אחת
- 😴 טיימרים חכמים
- 📊 סיכומים אוטומטיים
- 🗣 שליטה קולית עם Siri
- 📱 Widget על מסך הבית

**זה הכל!** פשוט, מהיר, ועובד מצוין 🚀
