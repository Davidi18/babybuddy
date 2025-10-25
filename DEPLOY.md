# 🚀 דיפלוי מהיר על Coolify

## צעדים מהירים

### 1️⃣ צור פרויקט חדש ב-Coolify

1. **התחבר ל-Coolify** שלך
2. **New Project** → **Git Repository**
3. **בחר את ה-Repository:** `Davidi18/babybuddy`
4. **Branch:** `master`

---

### 2️⃣ הגדר Persistent Volume (חובה!)

⚠️ **ללא זה כל הנתונים יימחקו בכל deployment!**

```
Project → Storage → Add Persistent Storage
```

**הגדרות:**
- **Name:** `babybuddy-data`
- **Destination Path:** `/data`
- **שמור**

---

### 3️⃣ הגדר משתני סביבה

```
Project → Environment Variables
```

**העתק והדבק:**

```bash
# === Admin User (חובה) ===
ADMIN_USERNAME=admin
ADMIN_PASSWORD=YourSecurePassword123!
ADMIN_EMAIL=your@email.com

# === Django (חובה) ===
DJANGO_SETTINGS_MODULE=babybuddy.settings.base
SECRET_KEY=django-insecure-GENERATE-RANDOM-KEY-50-CHARS
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# === Security (חובה) ===
CSRF_TRUSTED_ORIGINS=https://your-domain.com
SECURE_PROXY_SSL_HEADER=true

# === Hebrew Support (מומלץ) ===
TIME_ZONE=Asia/Jerusalem
LANGUAGE_CODE=he

# === Database - SQLite ===
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=/data/db.sqlite3
```

**ליצירת SECRET_KEY חדש:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

### 4️⃣ Deploy!

לחץ על **Deploy** 🚀

Coolify יבצע אוטומטית:
- ✅ בניית Docker Image
- ✅ התקנת תלויות
- ✅ הרצת Migrations
- ✅ Collect Static Files
- ✅ יצירת משתמש Admin
- ✅ הפעלת השרת

---

### 5️⃣ התחבר למערכת

1. **פתח:** `https://your-domain.com/admin/`
2. **התחבר:**
   - Username: מה שהגדרת ב-`ADMIN_USERNAME`
   - Password: מה שהגדרת ב-`ADMIN_PASSWORD`

---

## בדיקת Volume

**חשוב לבדוק שה-Volume עובד:**

1. התחבר למערכת
2. הוסף ילד חדש
3. עשה **Deploy** מחדש ב-Coolify
4. **התחבר שוב** - הילד צריך להיות שם!

❌ אם הילד נעלם = ה-Volume לא מוגדר נכון

---

## 🎯 אופציונלי: PostgreSQL (מומלץ לפרודקשן)

במקום SQLite, אפשר להשתמש ב-PostgreSQL:

1. **ב-Coolify:** `Project → Add Resource → Database → PostgreSQL`
2. **העתק את פרטי החיבור** (Coolify נותן אוטומטית)
3. **שנה משתני סביבה:**

```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=babybuddy
DB_USER=<מ-Coolify>
DB_PASSWORD=<מ-Coolify>
DB_HOST=<מ-Coolify>
DB_PORT=5432
```

4. **Deploy מחדש**

---

## 🆘 פתרון בעיות

### לא מצליח להתחבר?

```bash
# ב-Coolify Console:
python manage.py changepassword admin
```

### שגיאת CSRF?

הוסף:
```bash
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### שגיאת DisallowedHost?

הוסף את הדומיין ל:
```bash
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### המידע נמחק אחרי Deploy?

בדוק ש-Persistent Volume מוגדר נכון עם `/data`

---

## 📚 מסמכים נוספים

- [COOLIFY_SETUP.md](COOLIFY_SETUP.md) - מדריך מפורט מלא
- [README.md](README.md) - תיעוד הפרויקט

---

## ✅ Checklist מהיר

- [ ] פרויקט נוצר ב-Coolify מ-Git Repository
- [ ] Persistent Volume מוגדר ל-`/data`
- [ ] משתני סביבה הוגדרו (ADMIN_*, SECRET_KEY, ALLOWED_HOSTS)
- [ ] Deploy הצליח ללא שגיאות
- [ ] התחברות ל-`/admin/` עובדת
- [ ] הוספת ילד ו-Deploy נוסף - הילד נשאר

**כל הסימונים V? מעולה! המערכת פועלת! 🎉**
