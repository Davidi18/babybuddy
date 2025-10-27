# ✅ צ'קליסט לפני דיפלוי

## 🔴 קריטי - עשה את זה לפני הדיפלוי הבא!

### 1. עדכן משתני ENV ב-Coolify

**מחק את המשתנה הזה:**

- ❌ `DISABLE_COLLECTSTATIC=1` **← מחק אותו!**

**השאר/עדכן את אלה:**

```env
ADMIN_PASSWORD=admin123
ADMIN_USERNAME=admin
ALLOWED_HOSTS=*
CSRF_TRUSTED_ORIGINS=https://baby.davidvmayer.com
DEBUG=True
DJANGO_SETTINGS_MODULE=babybuddy.settings.development
LANGUAGE_CODE=he
SECRET_KEY=gN7pY3qzM8wVhF9kC2xT1rL5sZ0bE4jD6nUqA7yH9mR3pV8
TIME_ZONE=Asia/Jerusalem
```

**לא צריך יותר:**

- ❌ `STATICFILES_STORAGE` - מיותר, נוהל אוטומטית

---

## 🚀 שלבי הדיפלוי

### שלב 1: Merge הקוד

```bash
# מרג' את הבראנץ' לבראנץ' הראשי שלך
git checkout master  # או הבראנץ' שCoolify משתמש בו
git merge claude/debug-deployment-issues-011CUXtdHooMk8F8zNafR2Qb
git push origin master
```

### שלב 2: עדכן את Coolify

1. היכנס ל-Coolify dashboard
2. לך להגדרות Environment Variables
3. **מחק** את `DISABLE_COLLECTSTATIC=1`
4. שמור את השינויים

### שלב 3: Deploy

1. לחץ על כפתור **Deploy**
2. המתן שה-build יסתיים
3. בדוק את הלוגים

---

## 🔍 בדיקה אחרי דיפלוי

### 1. בדוק את הלוגים

```bash
docker logs baby --tail 50
```

**אתה אמור לראות:**

```
🚀 Starting Baby Buddy...
⏳ Waiting for database...
✅ Database ready
📦 Running migrations...
🎨 Collecting static files...
💾 Setting up cache...
👤 Setting up admin user...

✅ Ready! Starting server...
   DEBUG: True
   LANGUAGE: he
```

### 2. בדוק שהאתר עולה

- גלוש ל-https://baby.davidvmayer.com
- התחבר עם `admin` / `admin123`
- ודא שהעיצוב עובד (CSS/JS)

### 3. בדוק שאין CSRF errors

- נסה לשמור משהו
- אם יש CSRF error - ודא ש-`DJANGO_SETTINGS_MODULE=babybuddy.settings.development`

---

## 🚨 אם משהו לא עובד

### בעיה: האתר לא עולה בכלל

```bash
# בדוק שהקונטיינר רץ
docker ps | grep baby

# אם לא רץ, ראה למה
docker logs baby
```

### בעיה: אין עיצוב (CSS/JS לא עובדים)

זה אומר ש-collectstatic לא רץ או נכשל.

**פתרון:**

1. ודא ש-`DISABLE_COLLECTSTATIC` **לא קיים** ב-ENV
2. הרץ ידנית:

```bash
docker exec baby python manage.py collectstatic --noinput --clear
docker restart baby
```

### בעיה: CSRF errors

**פתרון:**

1. ודא `DJANGO_SETTINGS_MODULE=babybuddy.settings.development` ב-ENV
2. ודא `DEBUG=True` ב-ENV
3. Restart:

```bash
docker restart baby
```

### בעיה: Bad Gateway

```bash
# Restart proxy
docker restart coolify-proxy
```

---

## 📝 הבדלים לפני/אחרי

### לפני:

- ✋ הרץ migrations ידנית
- ✋ הרץ collectstatic ידנית
- ✋ תקן CSRF ידנית
- ✋ הורד static מGitHub ידנית
- ✋ Restart ידנית

### אחרי:

- ✅ **רק Deploy והכל אוטומטי!**

---

## 💡 טיפ חשוב

אם תרצה לחזור לעבודה בפרודקשן (לא development):

1. שנה `DJANGO_SETTINGS_MODULE=babybuddy.settings.production`
2. שנה `DEBUG=False`
3. **הפעל בחזרה את CSRF** (זה יופעל אוטומטית כשלא ב-development mode)

אבל כרגע, נשאר ב-development mode עם CSRF מבוטל.
