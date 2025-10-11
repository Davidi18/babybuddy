# 🚀 Baby Buddy על Coolify - מדריך התקנה

## 📋 תוכן עניינים
1. [משתני סביבה נדרשים](#משתני-סביבה-נדרשים)
2. [יצירת Superuser](#יצירת-superuser)
3. [הגדרות בסיס נתונים](#הגדרות-בסיס-נתונים)
4. [הגדרות אבטחה](#הגדרות-אבטחה)
5. [פקודות ראשוניות](#פקודות-ראשוניות)

---

## 🔧 משתני סביבה נדרשים

### 1️⃣ משתני Admin (Superuser)

ב-Coolify, הגדר את משתני הסביבה הבאים:

```bash
# פרטי משתמש Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password_here
ADMIN_EMAIL=your_email@example.com
```

**חשוב:**
- ✅ שנה את הסיסמה לסיסמה חזקה!
- ✅ השתמש באימייל אמיתי
- ✅ שמור את הפרטים במקום בטוח

---

### 2️⃣ משתני Django בסיסיים

```bash
# הגדרות Django
DJANGO_SETTINGS_MODULE=babybuddy.settings.base
SECRET_KEY=your_very_long_random_secret_key_here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# שפה וזמן
TIME_ZONE=Asia/Jerusalem
LANGUAGE_CODE=he
```

**ליצירת SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### 3️⃣ הגדרות בסיס נתונים

אם אתה משתמש ב-PostgreSQL (מומלץ):

```bash
# PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=babybuddy
DB_USER=babybuddy_user
DB_PASSWORD=your_db_password_here
DB_HOST=postgres
DB_PORT=5432
```

אם אתה משתמש ב-SQLite (פשוט יותר):

```bash
# SQLite (ברירת מחדל)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=/data/db.sqlite3
```

---

## 👤 יצירת Superuser

### אופציה 1: אוטומטית עם משתני סביבה (מומלץ!)

הפרויקט כבר כולל סקריפט אוטומטי: `scripts/init_admin.py`

**איך זה עובד:**
1. הגדר משתני סביבה ב-Coolify:
   ```bash
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=YourSecurePassword123!
   ADMIN_EMAIL=your@email.com
   ```

2. הרץ את הסקריפט אחרי ה-deployment:
   ```bash
   python scripts/init_admin.py
   ```

3. זהו! המשתמש נוצר אוטומטית.

**הסקריפט:**
- ✅ בודק אם המשתמש כבר קיים
- ✅ יוצר superuser עם הפרטים מה-ENV
- ✅ לא יוצר כפילויות

---

### אופציה 2: ידנית דרך Django

אם אתה רוצה ליצור ידנית:

```bash
# התחבר לקונטיינר ב-Coolify
python manage.py createsuperuser

# או עם פרטים ישירות:
python manage.py createsuperuser \
  --username admin \
  --email admin@example.com \
  --noinput
```

ואז הגדר סיסמה:
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='admin')
>>> user.set_password('YourSecurePassword123!')
>>> user.save()
>>> exit()
```

---

### אופציה 3: דרך Django Shell (הכי גמיש)

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# יצירת superuser
admin = User.objects.create_superuser(
    username='admin',
    email='admin@example.com',
    password='YourSecurePassword123!'
)

print(f'✅ Superuser created: {admin.username}')
```

---

## 🔐 שינוי סיסמה למשתמש קיים

אם המשתמש כבר קיים ואתה רוצה לשנות סיסמה:

```bash
python manage.py changepassword admin
```

או דרך shell:

```python
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='admin')
user.set_password('NewSecurePassword123!')
user.save()
print('✅ Password changed!')
```

---

## 📦 פקודות ראשוניות ב-Coolify

### סדר הפעולות:

```bash
# 1. הרצת migrations
python manage.py migrate

# 2. יצירת superuser (אוטומטי)
python scripts/init_admin.py

# 3. איסוף קבצים סטטיים
python manage.py collectstatic --noinput

# 4. קומפילציה של תרגומים
python manage.py compilemessages -l he

# 5. הרצת השרת
gunicorn babybuddy.wsgi:application --bind 0.0.0.0:8000
```

---

## 🎯 דוגמת משתני סביבה מלאה ל-Coolify

העתק את זה ל-Coolify Environment Variables:

```bash
# === Admin User ===
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourVerySecurePassword123!@#
ADMIN_EMAIL=your.email@example.com

# === Django Settings ===
DJANGO_SETTINGS_MODULE=babybuddy.settings.base
SECRET_KEY=django-insecure-CHANGE-THIS-TO-RANDOM-STRING-50-CHARS-LONG
DEBUG=False
ALLOWED_HOSTS=babybuddy.yourdomain.com,www.babybuddy.yourdomain.com

# === Localization ===
TIME_ZONE=Asia/Jerusalem
LANGUAGE_CODE=he

# === Database (SQLite) ===
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=/data/db.sqlite3

# === או Database (PostgreSQL) ===
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=babybuddy
# DB_USER=babybuddy_user
# DB_PASSWORD=your_db_password_here
# DB_HOST=postgres
# DB_PORT=5432

# === Security ===
CSRF_TRUSTED_ORIGINS=https://babybuddy.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 🚀 התחברות ראשונה

1. **פתח את האתר:**
   ```
   https://babybuddy.yourdomain.com/admin/
   ```

2. **התחבר עם:**
   - Username: `admin` (או מה שהגדרת)
   - Password: הסיסמה שהגדרת ב-`ADMIN_PASSWORD`

3. **הוסף ילד ראשון:**
   - לחץ על שם המשתמש (פינה ימנית עליונה)
   - Site → Children
   - Add Child

---

## 🔄 עדכון Superuser קיים

אם אתה רוצה לעדכן משתמש admin קיים:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model

User = get_user_model()

# מצא את המשתמש
admin = User.objects.get(username='admin')

# עדכן פרטים
admin.email = 'new.email@example.com'
admin.set_password('NewPassword123!')
admin.is_superuser = True
admin.is_staff = True
admin.save()

print('✅ Admin updated!')
```

---

## 🛠️ פתרון בעיות

### בעיה: לא יכול להתחבר

**פתרון 1: אפס סיסמה**
```bash
python manage.py changepassword admin
```

**פתרון 2: בדוק אם המשתמש קיים**
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(username='admin').exists()
True  # אם False, המשתמש לא קיים
>>> User.objects.filter(username='admin').first()
<User: admin>  # פרטי המשתמש
```

**פתרון 3: צור מחדש**
```bash
python scripts/init_admin.py
```

---

### בעיה: "CSRF verification failed"

הוסף ל-Environment Variables:
```bash
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

---

### בעיה: "DisallowedHost"

הוסף את הדומיין ל-ALLOWED_HOSTS:
```bash
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost
```

---

## 📝 טיפים חשובים

### 1. סיסמה חזקה
✅ לפחות 12 תווים
✅ אותיות גדולות וקטנות
✅ מספרים
✅ תווים מיוחדים (!@#$%^&*)

### 2. גיבוי
💾 גבה את בסיס הנתונים באופן קבוע:
```bash
# SQLite
cp /data/db.sqlite3 /backups/db-$(date +%Y%m%d).sqlite3

# PostgreSQL
pg_dump babybuddy > backup-$(date +%Y%m%d).sql
```

### 3. אבטחה
🔒 השתמש ב-HTTPS תמיד
🔒 הגדר `DEBUG=False` בפרודקשן
🔒 שמור `SECRET_KEY` בסוד
🔒 עדכן סיסמאות באופן קבוע

---

## 🎉 סיכום

### מה צריך להגדיר ב-Coolify:

1. **משתני סביבה:**
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `ADMIN_EMAIL`
   - `SECRET_KEY`
   - `ALLOWED_HOSTS`

2. **פקודות ראשוניות:**
   ```bash
   python manage.py migrate
   python scripts/init_admin.py
   python manage.py collectstatic --noinput
   ```

3. **התחבר:**
   - URL: `https://your-domain.com/admin/`
   - Username: מה שהגדרת ב-`ADMIN_USERNAME`
   - Password: מה שהגדרת ב-`ADMIN_PASSWORD`

**זהו! המערכת מוכנה לשימוש!** 🚀

---

## 📞 עזרה נוספת

- 📖 [תיעוד Django](https://docs.djangoproject.com/)
- 📖 [תיעוד Coolify](https://coolify.io/docs)
- 💬 [Baby Buddy GitHub](https://github.com/babybuddy/babybuddy)

**שאלות? בעיות? פתח issue או שלח הודעה!** 💬
