# 🔐 איך לאפס/לשנות סיסמת Admin

## 📝 סיכום מהיר

**כן! משתני ה-ENV ב-Coolify שולטים על סיסמת ה-Admin.**

הסקריפט `init_admin.py` רץ בכל deployment ו**מעדכן אוטומטית** את:

- ✅ הסיסמה
- ✅ האימייל
- ✅ הרשאות superuser

---

## 🔄 דרך 1: עדכון דרך Coolify (מומלץ!)

### צעדים:

1. **פתח את הפרויקט ב-Coolify**
2. **עבור ל-Environment Variables**
3. **שנה את המשתנים:**
   ```bash
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=הסיסמה-החדשה-שלך-123!
   ADMIN_EMAIL=newemail@example.com
   ```
4. **שמור את השינויים**
5. **לחץ על Deploy** או **Restart**

### מה קורה?

```
Deploy → Procfile.sh → init_admin.py
                       ↓
              קורא את ה-ENV החדש
                       ↓
              מוצא שהמשתמש קיים
                       ↓
              מעדכן סיסמה + אימייל
                       ↓
                    ✅ סיום!
```

### ⏱️ כמה זמן זה לוקח?

- **עדכון ENV:** מיידי
- **Deploy/Restart:** 1-3 דקות
- **סיסמה מעודכנת:** מיד אחרי שה-deployment הסתיים

---

## 🖥️ דרך 2: עדכון ידני בקונסול

אם אתה לא רוצה לעשות deploy מחדש:

### בקונסול של Coolify:

```bash
# התחבר לקונטיינר
cd /app

# הרץ Django shell
python manage.py shell
```

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# מצא את המשתמש
admin = User.objects.get(username='admin')

# שנה סיסמה
admin.set_password('הסיסמה-החדשה-שלך')
admin.save()

print('✅ הסיסמה שונתה בהצלחה!')
exit()
```

או בשורה אחת:

```bash
python manage.py changepassword admin
```

### ⚠️ חשוב לדעת:

**שינוי ידני בקונסול הוא זמני!**

- ✅ עובד מיד
- ❌ ידרוס ב-deployment הבא (אם ENV שונה)

**למה?**
כי ב-deployment הבא, `init_admin.py` ירוץ שוב ויעדכן את הסיסמה למה שב-ENV!

**פתרון:** תמיד עדכן גם את ה-ENV ב-Coolify!

---

## 🔄 תרחישים נפוצים

### תרחיש 1: שכחתי את הסיסמה

**פתרון מהיר:**

1. פתח Coolify → Environment Variables
2. שנה `ADMIN_PASSWORD=סיסמה-חדשה-123`
3. Deploy/Restart
4. ✅ התחבר עם הסיסמה החדשה

---

### תרחיש 2: רוצה להחליף username

**אופציה א': יצירת משתמש חדש**

ב-Coolify ENV:

```bash
ADMIN_USERNAME=david  # שם חדש
ADMIN_PASSWORD=password123
```

Deploy → **ייצור משתמש חדש** בשם `david`

⚠️ המשתמש הישן (`admin`) ישאר קיים!

**אופציה ב': שינוי username קיים**

בקונסול:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='admin')
user.username = 'david'
user.save()
```

ואז עדכן ב-ENV:

```bash
ADMIN_USERNAME=david
```

---

### תרחיש 3: יצירת משתמש admin נוסף

ב-Coolify Console:

```bash
python manage.py createsuperuser
```

או:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

User.objects.create_superuser(
    username='sarah',
    email='sarah@example.com',
    password='sarah_password_123'
)
```

⚠️ משתמש נוסף **לא** מושפע מ-ENV - רק המשתמש ב-`ADMIN_USERNAME` מעודכן.

---

## 🛡️ Best Practices

### 1. השתמש ב-ENV תמיד

✅ **נכון:**

```
Coolify ENV → ADMIN_PASSWORD=new_pass → Deploy
```

❌ **לא מומלץ:**

```
Console → change password → (ידרוס בdeployment הבא)
```

### 2. סיסמה חזקה

```bash
# טוב
ADMIN_PASSWORD=MyBaby2025!SecurePass

# לא טוב
ADMIN_PASSWORD=admin
```

### 3. שנה סיסמה אחרי deployment ראשון

אחרי הinstallation הראשון, **מיד** שנה את הסיסמה ל-ENV!

### 4. גיבוי פרטי הגישה

שמור את פרטי ה-admin במנהל סיסמאות:

- Username
- Password
- Email
- URL של האתר

---

## 🔍 בדיקות

### בדוק שהעדכון עבד:

1. **התחבר ל-Coolify Logs**
2. **חפש את השורה:**

   ```
   🔄 משתמש admin עודכן: admin
   ```

   או

   ```
   ✅ משתמש admin נוצר בהצלחה: admin
   ```

3. **נסה להתחבר:**
   - URL: `https://your-domain.com/admin/`
   - Username: מה שב-`ADMIN_USERNAME`
   - Password: מה שב-`ADMIN_PASSWORD`

### אם ההתחברות נכשלת:

1. **בדוק שה-deployment הצליח** (אין שגיאות ב-logs)
2. **בדוק שה-ENV נשמר נכון** (אין רווחים מיותרים)
3. **נסה reset ידני בקונסול** (דרך 2 למעלה)

---

## 🆘 פתרון בעיות

### בעיה: "לא מצליח להתחבר"

**פתרון 1:** אפס דרך ENV

```bash
Coolify → ENV → שנה ADMIN_PASSWORD → Deploy
```

**פתרון 2:** אפס בקונסול

```bash
python manage.py changepassword admin
```

### בעיה: "המשתמש לא קיים"

בדוק ב-logs:

```bash
# אם אתה רואה:
✅ משתמש admin נוצר

# אבל עדיין לא עובד, בדוק בקונסול:
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(username='admin').exists()
True  # אם False - המשתמש באמת לא קיים!
```

אם `False`, צור ידנית:

```bash
python scripts/init_admin.py
```

### בעיה: "הסיסמה מתאפסת כל פעם"

זה קורה כי:

- ENV מכיל סיסמה ישנה
- בכל deployment הסקריפט מעדכן לפי ENV

**פתרון:**
עדכן את `ADMIN_PASSWORD` ב-ENV למה שאתה רוצה!

---

## 📋 Checklist לשינוי סיסמה

- [ ] פתחתי את Coolify
- [ ] עברתי ל-Environment Variables
- [ ] שיניתי את `ADMIN_PASSWORD` לסיסמה חדשה
- [ ] (אופציונלי) עדכנתי `ADMIN_EMAIL`
- [ ] שמרתי את השינויים
- [ ] לחצתי על Deploy/Restart
- [ ] המתנתי לסיום ה-deployment (1-3 דקות)
- [ ] התחברתי לאתר עם הסיסמה החדשה
- [ ] ✅ זה עובד!

---

## 💡 טיפ פרו

### סקריפט מהיר לאיפוס (בקונסול):

שמור את זה לשימוש חוזר:

```bash
#!/bin/bash
# reset_admin.sh

python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('$1')  # $1 = הסיסמה מהארגומנט
admin.save()
print('✅ סיסמה שונתה ל:', '$1')
EOF
```

שימוש:

```bash
bash reset_admin.sh הסיסמה-החדשה-שלך
```

---

## 🎯 סיכום

| דרך                | זמן     | עמידות               | מומלץ?       |
| ------------------ | ------- | -------------------- | ------------ |
| עדכון ENV + Deploy | 2-3 דק' | קבוע (לא נמחק)       | ✅ כן!       |
| שינוי בקונסול      | מיידי   | זמני (ידרוס בdeploy) | ⚠️ רק לחירום |
| `changepassword`   | מיידי   | זמני (ידרוס בdeploy) | ⚠️ רק לחירום |

**המלצה:** **תמיד** עדכן דרך ENV ב-Coolify!

---

## 📞 עזרה נוספת

- [COOLIFY_SETUP.md](COOLIFY_SETUP.md) - מדריך התקנה מלא
- [DEPLOY.md](DEPLOY.md) - הנחיות deployment
- [Django User Management](https://docs.djangoproject.com/en/5.0/topics/auth/)

**שאלות? בעיות? תיצור issue או שלח הודעה!** 💬
