#!/bin/bash
# Baby Buddy - Database Backup Script
# Run this BEFORE making any changes if you don't have persistent storage!

set -e

echo "🔍 Searching for Baby Buddy container..."

# Find the container
CONTAINER=$(docker ps | grep babybuddy | awk '{print $1}' | head -1)

if [ -z "$CONTAINER" ]; then
    echo "❌ No Baby Buddy container found!"
    echo "   Make sure the app is running."
    exit 1
fi

echo "✅ Found container: $CONTAINER"

# Create backup directory
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

# Backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sqlite3"

echo "📦 Backing up database..."

# Copy database from container
docker cp "$CONTAINER:/data/db.sqlite3" "$BACKUP_FILE"

if [ -f "$BACKUP_FILE" ]; then
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup completed successfully!"
    echo "   File: $BACKUP_FILE"
    echo "   Size: $FILE_SIZE"
    echo ""
    echo "💡 To restore this backup:"
    echo "   docker cp $BACKUP_FILE <new-container>:/data/db.sqlite3"
else
    echo "❌ Backup failed!"
    exit 1
fi

echo ""
echo "🎉 Done! Your data is safe."
