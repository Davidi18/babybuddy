#!/bin/bash
# Script to update Baby Buddy logo
# Usage: ./update_logo.sh /path/to/your/logo.png

set -e

if [ -z "$1" ]; then
    echo "❌ Error: Please provide path to logo image"
    echo "Usage: ./update_logo.sh /path/to/your/logo.png"
    exit 1
fi

LOGO_PATH="$1"

if [ ! -f "$LOGO_PATH" ]; then
    echo "❌ Error: File not found: $LOGO_PATH"
    exit 1
fi

echo "🎨 Updating Baby Buddy logo..."
echo "📁 Source: $LOGO_PATH"

# Target directory
TARGET_DIR="babybuddy/static_src/logo"

# Backup old logos
echo "💾 Backing up old logos..."
mkdir -p "${TARGET_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
cp ${TARGET_DIR}/*.png "${TARGET_DIR}/backup_$(date +%Y%m%d_%H%M%S)/" 2>/dev/null || true

# Create different sizes
echo "🔧 Creating icon-brand.png (60x60)..."
convert "$LOGO_PATH" -resize 60x60 -background none -gravity center -extent 60x60 "${TARGET_DIR}/icon-brand.png"

echo "🔧 Creating icon.png (128x128)..."
convert "$LOGO_PATH" -resize 128x128 -background none -gravity center -extent 128x128 "${TARGET_DIR}/icon.png"

echo "🔧 Creating logo.png (256x256)..."
convert "$LOGO_PATH" -resize 256x256 -background none -gravity center -extent 256x256 "${TARGET_DIR}/logo.png"

echo "🔧 Creating logo-sad.png (128x128)..."
# For now, just copy the same logo. You can edit this later to add a sad face
convert "$LOGO_PATH" -resize 128x128 -background none -gravity center -extent 128x128 "${TARGET_DIR}/logo-sad.png"

# Copy to static directory as well
echo "📋 Copying to static directory..."
cp ${TARGET_DIR}/*.png babybuddy/static/babybuddy/logo/

echo "✅ Logo updated successfully!"
echo ""
echo "📝 Files created:"
ls -lh ${TARGET_DIR}/*.png
echo ""
echo "🔄 Next steps:"
echo "1. Restart the development server"
echo "2. Run: python manage.py collectstatic --noinput"
echo "3. Refresh your browser"
echo ""
echo "💡 Tip: Edit logo-sad.png manually to add a sad face for error pages"
