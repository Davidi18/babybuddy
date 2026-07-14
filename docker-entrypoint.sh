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

# 2. Compile translation messages
echo "🌐 Compiling translations..."
python manage.py compilemessages 2>/dev/null || echo "⚠️  Could not compile messages (gettext not installed)"

# 3. Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# 4. Collect static files
#
# Static files are normally baked into the image at build time (see Dockerfile),
# which guarantees the hashed filenames served with "Cache-Control: immutable"
# are identical across every container and restart. Only (re)collect here if the
# manifest is missing - e.g. when the image was built without the build step or
# static is mounted on an empty volume. Re-running unconditionally on every boot
# can regenerate hashes and leave clients referencing assets that 404 (the app
# then loads unstyled), so we skip it when a manifest already exists.
echo "🎨 Checking static files..."
if [ -f "/app/static/staticfiles.json" ]; then
    echo "✅ Static files already collected (baked into image)"
else
    echo "📥 No manifest found - collecting static files..."
    python manage.py collectstatic --noinput --clear
fi

# 6. Create cache table
echo "💾 Setting up cache..."
python manage.py createcachetable cache_default 2>/dev/null || true

# 7. Create admin user
echo "👤 Setting up admin user..."
python /app/scripts/init_admin.py 2>/dev/null || true

echo ""
echo "✅ Ready! Starting server..."
echo "   DEBUG: ${DEBUG:-False}"
echo "   LANGUAGE: ${LANGUAGE_CODE:-en-US}"
echo ""

# 8. Start Gunicorn
exec gunicorn babybuddy.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-30} \
    --access-logfile - \
    --error-logfile - \
    --log-level ${GUNICORN_LOG_LEVEL:-info}
