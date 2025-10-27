# 🚀 Baby Buddy על Coolify - מדריך התקנה

## 📋 תוכן עניינים

1. [Persistent Volume (חובה!)](#persistent-volume-חובה)
2. [משתני סביבה נדרשים](#משתני-סביבה-נדרשים)
3. [יצירת Superuser](#יצירת-superuser)
4. [הגדרות בסיס נתונים](#הגדרות-בסיס-נתונים)
5. [הגדרות אבטחה](#הגדרות-אבטחה)
6. [פקודות ראשוניות](#פקודות-ראשוניות)

---

## 💾 Persistent Volume (חובה!)

### ⚠️ למה זה קריטי?

**ללא Persistent Volume, כל המידע יימחק בכל deploy!**

כשאתה משתמש ב-SQLite (ברירת המחדל), בסיס הנתונים נשמר בקובץ `db.sqlite3` בתוך הקונטיינר.
אם אין Persistent Volume, הקובץ הזה נמחק בכל פעם שיש deployment חדש.

**מה זה אומר?**

- ❌ כל הילדים שהוספת - נמחקים
- ❌ כל הפעילויות (האכלות, שינה, חיתולים) - נמחקות
- ❌ משתמש ה-admin - נמחק
- ❌ כל ההגדרות - נמחקות

### 📁 איך להגדיר ב-Coolify

#### שלב 1: פתח את הפרויקט ב-Coolify

לאחר יצירת הפרויקט, לך ל:

```
Project → Storage → Add Persistent Storage
```

#### שלב 2: הגדר את ה-Volume

מלא את הפרטים הבאים:

**Name (שם):**

```
babybuddy-data
```

**Source Path (נתיב במחשב המארח):**

```
/data/coolify/babybuddy/data
```

או השאר ריק - Coolify יבחר אוטומטית.

**Destination Path (נתיב בקונטיינר) - חשוב מאוד!:**

```
/data
```

**⚠️ חשוב:** הנתיב `/data` הוא בדיוק המקום שבו Baby Buddy שומר את בסיס הנתונים!

#### שלב 3: שמור ועשה Deploy

לחץ על **Save** ואז **Deploy** מחדש.

### 🔍 איך לוודא שזה עובד?

אחרי ה-deployment:

1. התחבר לאתר והוסף ילד
2. עשה **Deploy** נוסף (או Restart)
3. התחבר שוב - הילד צריך להיות שם!

אם הילד נעלם = ה-Volume לא מוגדר נכון.

---

### 📊 אופציה: PostgreSQL במקום SQLite

אם אתה רוצה פתרון יותר מקצועי, השתמש ב-PostgreSQL:

**יתרונות:**

- ✅ ביצועים טובים יותר
- ✅ תמיכה במספר משתמשים במקביל
- ✅ גיבויים קלים יותר
- ✅ Coolify מנהל את זה בשבילך

**איך להגדיר:**

1. **ב-Coolify, הוסף PostgreSQL Database:**

   ```
   Project → Add Resource → Database → PostgreSQL
   ```

2. **העתק את פרטי החיבור** (Coolify נותן לך אותם אוטומטית)

3. **הוסף משתני סביבה:**

   ```bash
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=babybuddy
   DB_USER=<מ-Coolify>
   DB_PASSWORD=<מ-Coolify>
   DB_HOST=<מ-Coolify>
   DB_PORT=5432
   ```

4. **Deploy** - Django יצור את הטבלאות אוטומטית!

**עם PostgreSQL אתה עדיין צריך Volume ל:**

- תמונות שמשתמשים מעלים
- קבצים סטטיים (אם לא משתמש ב-CDN)

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

## 👤 יצירת Superuser (משתמש ראשי)

### 🤔 מה זה Superuser?

**Superuser** (או Admin) הוא המשתמש הראשי שיכול:

- ✅ להתחבר לממשק הניהול (`/admin/`)
- ✅ להוסיף ילדים
- ✅ לנהל משתמשים אחרים
- ✅ לראות ולערוך את כל המידע
- ✅ לשנות הגדרות מערכת

**בלי Superuser - לא תוכל להשתמש באפליקציה!**

---

### אופציה 1: אוטומטית עם משתני סביבה (מומלץ! ✨)

הפרויקט כבר כולל סקריפט אוטומטי: `scripts/init_admin.py`

**ה-`Procfile.sh` שלנו מריץ את זה אוטומטית בכל deployment!**

**איך זה עובד:**

#### שלב 1: הגדר משתני סביבה ב-Coolify

לך ל: `Project → Environment Variables` והוסף:

```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourSecurePassword123!
ADMIN_EMAIL=your@email.com
```

**⚠️ חשוב:**

- השתמש בסיסמה **חזקה** (לפחות 8 תווים, אותיות גדולות/קטנות, מספרים, תווים מיוחדים)
- שמור את הפרטים במקום בטוח (מנהל סיסמאות)
- אל תשתף את הסיסמה!

#### שלב 2: Deploy

לחץ על **Deploy** - הסקריפט יצור את המשתמש אוטומטית!

#### שלב 3: התחבר

1. פתח: `https://your-domain.com/admin/`
2. התחבר עם:
   - **Username:** מה שהגדרת ב-`ADMIN_USERNAME`
   - **Password:** מה שהגדרת ב-`ADMIN_PASSWORD`

**הסקריפט:**

- ✅ רץ אוטומטית בכל deployment
- ✅ בודק אם המשתמש כבר קיים
- ✅ יוצר superuser עם הפרטים מה-ENV
- ✅ לא יוצר כפילויות
- ✅ לא משנה סיסמה למשתמש קיים (בטיחות!)

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
✅ תווים מיוחדים (!@#$%^&\*)

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

## 🎉 סיכום מהיר - צ'קליסט לדיפלוי

### ✅ צ'קליסט - עשה את זה לפני Deploy:

#### 1. **הגדר Persistent Volume (חובה!)**

```
Project → Storage → Add Persistent Storage
Name: babybuddy-data
Destination Path: /data
```

#### 2. **הגדר משתני סביבה:**

**חובה:**

```bash
# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<סיסמה חזקה>
ADMIN_EMAIL=your@email.com

# Django
SECRET_KEY=<הפעל: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
ALLOWED_HOSTS=your-domain.com
DEBUG=False

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

**מומלץ:**

```bash
TIME_ZONE=Asia/Jerusalem
LANGUAGE_CODE=he
```

#### 3. **Deploy!**

לחץ על **Deploy** - הכל יקרה אוטומטית:

- ✅ Migrations
- ✅ Collect Static Files
- ✅ Create Admin User
- ✅ Start Server

#### 4. **התחבר:**

- URL: `https://your-domain.com/admin/`
- Username: מה שהגדרת ב-`ADMIN_USERNAME`
- Password: מה שהגדרת ב-`ADMIN_PASSWORD`

#### 5. **בדוק שה-Volume עובד:**

- הוסף ילד
- עשה Deploy מחדש
- הילד צריך להישאר!

**זהו! המערכת מוכנה לשימוש!** 🚀

---

### 🆘 עזרה מהירה

**לא מצליח להתחבר?**

```bash
# התחבר לקונטיינר ב-Coolify ורוץ:
python manage.py changepassword admin
```

**המידע נמחק אחרי Deploy?**

- בדוק שה-Persistent Volume מוגדר ל-`/data`

**שגיאת CSRF?**

- הוסף `CSRF_TRUSTED_ORIGINS=https://your-domain.com`

**שגיאת DisallowedHost?**

- הוסף את הדומיין ל-`ALLOWED_HOSTS`

---

## 📞 עזרה נוספת

- 📖 [תיעוד Django](https://docs.djangoproject.com/)
- 📖 [תיעוד Coolify](https://coolify.io/docs)
- 💬 [Baby Buddy GitHub](https://github.com/babybuddy/babybuddy)

**שאלות? בעיות? פתח issue או שלח הודעה!** 💬
