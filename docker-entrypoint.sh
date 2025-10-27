#!/bin/bash
set -e

echo "🚀 Starting Baby Buddy..."

# 1. Wait for database to be ready (if using external DB)
echo "⏳ Waiting for database..."
max_retries=30
retry_count=0

while ! python manage.py check --database default > /dev/null 2>&1; do
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        echo "❌ Database connection failed"
        exit 1
    fi
    sleep 2
done

echo "✅ Database ready"

# 2. Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# 3. Download static files from GitHub if missing (to source location)
echo "📥 Checking static files..."
if [ ! -d "/app/babybuddy/static/babybuddy/css" ] || [ -z "$(ls -A /app/babybuddy/static/babybuddy/css 2>/dev/null)" ]; then
    echo "⚠️  Static files missing or empty, downloading from GitHub..."
    cd /app
    mkdir -p /app/babybuddy/static
    rm -rf /app/babybuddy/static/babybuddy
    curl -sL https://github.com/Davidi18/babybuddy/archive/refs/heads/master.tar.gz | tar -xz
    # העתק מהמיקום הנכון - babybuddy-master/babybuddy/static/babybuddy
    cp -r babybuddy-master/babybuddy/static/babybuddy /app/babybuddy/static/
    rm -rf babybuddy-master
    echo "✅ Static files downloaded to source location"
else
    echo "✅ Static files already exist in source"
fi

# 4. Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput --clear

# 5. Create cache table
echo "💾 Setting up cache..."
python manage.py createcachetable cache_default 2>/dev/null || true

# 6. Create admin user
echo "👤 Setting up admin user..."
python /app/scripts/init_admin.py 2>/dev/null || true

echo ""
echo "✅ Ready! Starting server..."
echo "   DEBUG: ${DEBUG:-False}"
echo "   LANGUAGE: ${LANGUAGE_CODE:-en-US}"
echo ""

# 7. Start Gunicorn
exec gunicorn babybuddy.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-30} \
    --access-logfile - \
    --error-logfile - \
    --log-level ${GUNICORN_LOG_LEVEL:-info}
