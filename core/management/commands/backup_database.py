# -*- coding: utf-8 -*-
"""
Management command לגיבוי אוטומטי של בסיס הנתונים
Automatic database backup management command
"""
import os
import json
from datetime import datetime

from django.core.management.base import BaseCommand
from django.core import serializers
from django.conf import settings

from core import models


class Command(BaseCommand):
    help = "גיבוי אוטומטי של כל נתוני Baby Buddy / Backup all Baby Buddy data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="backups",
            help="תיקיית יעד לגיבויים / Backup destination directory",
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["json", "xml"],
            default="json",
            help="פורמט הגיבוי / Backup format",
        )

    def handle(self, *args, **options):
        output_dir = options["output_dir"]
        backup_format = options["format"]

        # יצירת תיקייה אם לא קיימת
        os.makedirs(output_dir, exist_ok=True)

        # שם קובץ עם timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"babybuddy_backup_{timestamp}.{backup_format}"
        filepath = os.path.join(output_dir, filename)

        self.stdout.write(self.style.WARNING(f"מתחיל גיבוי... / Starting backup..."))

        # רשימת כל המודלים לגיבוי
        models_to_backup = [
            models.Child,
            models.Feeding,
            models.Sleep,
            models.DiaperChange,
            models.TummyTime,
            models.Temperature,
            models.Weight,
            models.Height,
            models.HeadCircumference,
            models.BMI,
            models.Note,
            models.Timer,
            models.Pumping,
            models.Tag,
        ]

        # איסוף כל הנתונים
        all_objects = []
        for model in models_to_backup:
            objects = model.objects.all()
            all_objects.extend(objects)
            self.stdout.write(
                f"  ✓ {model._meta.verbose_name_plural}: {objects.count()} רשומות"
            )

        # סיריאליזציה ושמירה
        try:
            serialized_data = serializers.serialize(backup_format, all_objects)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(serialized_data)

            # חישוב גודל קובץ
            file_size = os.path.getsize(filepath)
            file_size_mb = file_size / (1024 * 1024)

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅ גיבוי הושלם בהצלחה! / Backup completed successfully!"
                )
            )
            self.stdout.write(f"   קובץ: {filepath}")
            self.stdout.write(f"   גודל: {file_size_mb:.2f} MB")
            self.stdout.write(f'   סה"כ רשומות: {len(all_objects)}')

            # יצירת קובץ מטא-דאטה
            metadata = {
                "backup_date": datetime.now().isoformat(),
                "total_records": len(all_objects),
                "file_size_bytes": file_size,
                "format": backup_format,
                "models": {
                    model._meta.model_name: model.objects.count()
                    for model in models_to_backup
                },
            }

            metadata_file = filepath.replace(f".{backup_format}", f"_metadata.json")
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            self.stdout.write(f"   מטא-דאטה: {metadata_file}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ שגיאה בגיבוי / Backup error: {str(e)}")
            )
            raise

        return f"Backup saved to {filepath}"
