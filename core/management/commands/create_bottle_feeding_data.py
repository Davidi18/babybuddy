# -*- coding: utf-8 -*-
"""
Management command ליצירת נתוני דמה של הנקה בבקבוק בלבד
Create dummy data for bottle-only feeding
"""
from random import choice, choices, randint, uniform
from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils import timezone

from faker import Faker

from core import models


class Command(BaseCommand):
    help = "יוצר נתוני דמה של תינוקת שמניקים אותה רק בבקבוק (Generates dummy data for bottle-only feeding)"

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.faker = Faker(['he_IL'])  # עברית
        self.child = None
        self.time = None
        self.time_now = timezone.localtime()

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            dest="days",
            default=7,
            type=int,
            help="כמה ימים של נתונים ליצור (How many days of data to create)",
        )
        parser.add_argument(
            "--name",
            dest="name",
            default="",
            help="שם התינוקת (Baby's name)",
        )

    def handle(self, *args, **kwargs):
        verbosity = int(kwargs["verbosity"])
        days = int(kwargs["days"]) or 7
        baby_name = kwargs.get("name") or "נועה"

        # יצירת התינוקת (או מצא קיימת)
        birth_date = timezone.localdate() - timedelta(days=days)

        # נסה למצוא ילדה קיימת עם אותו שם
        existing_child = models.Child.objects.filter(first_name=baby_name).first()
        if existing_child:
            # מחק את הילדה הקיימת ואת כל הנתונים שלה
            if verbosity > 0:
                self.stdout.write(
                    self.style.WARNING(f'מוחק נתונים קיימים עבור "{existing_child.name()}"...')
                )
            existing_child.delete()

        self.child = models.Child.objects.create(
            first_name=baby_name,
            last_name="",
            birth_date=birth_date,
            feeding_mode='bottle_only',  # חשוב! זה מציין שהיא מניקה רק בבקבוק
        )
        self.child.save()

        if verbosity > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ נוצרה תינוקת בשם "{self.child.name()}" עם מצב הנקה: בקבוק בלבד'
                )
            )

        # הוספת נתוני דמה
        self._add_child_data(days)

        if verbosity > 0:
            feeding_count = models.Feeding.objects.filter(child=self.child).count()
            sleep_count = models.Sleep.objects.filter(child=self.child).count()
            diaper_count = models.DiaperChange.objects.filter(child=self.child).count()

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n📊 נוספו בהצלחה:\n'
                    f'   🍼 {feeding_count} האכלות בבקבוק\n'
                    f'   💤 {sleep_count} תקופות שינה\n'
                    f'   🧷 {diaper_count} החלפות חיתול\n'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🔗 כעת ניתן לבדוק את הוובהוקים ב:\n'
                    f'   /api/webhooks/daily-summary/?child={self.child.slug}\n'
                    f'   /api/webhooks/status/?child={self.child.slug}\n'
                    f'   /api/webhooks/alerts/?child={self.child.slug}\n'
                )
            )

    @transaction.atomic
    def _add_child_data(self, days):
        """
        מוסיף נתוני דמה לילדה מתאריך הלידה ועד עכשיו
        Adds dummy data from birth_date to now
        """
        self.time = timezone.make_aware(
            timezone.datetime.combine(
                self.child.birth_date,
                timezone.datetime.min.time()
            )
        )

        # דפוס יומי: שינה -> האכלה -> חיתול -> שינה -> האכלה...
        # Daily pattern: sleep -> feed -> diaper -> sleep -> feed...

        while self.time < self.time_now:
            # שינה (בלילה יותר ארוכה, ביום יותר קצרה)
            self._add_sleep_entry()

            # האכלה בבקבוק
            self._add_bottle_feeding()

            # חיתול
            if choice([True, True, False]):  # 66% סיכוי
                self._add_diaperchange_entry()

            # לפעמים עוד חיתול
            if choice([True, False, False, False]):  # 25% סיכוי
                self._add_diaperchange_entry()

    @transaction.atomic
    def _add_bottle_feeding(self):
        """
        מוסיף האכלה בבקבוק בלבד (bottle only feeding)
        """
        # כמות בבקבוק - בין 60 ל-150 מ"ל
        amount = Decimal(str(round(uniform(60.0, 150.0), 1)))

        # משך האכלה - בין 10 ל-25 דקות
        start = self.time + timedelta(minutes=randint(5, 30))
        duration_minutes = randint(10, 25)
        end = start + timedelta(minutes=duration_minutes)

        # סוג: חלב אם או תרכובת
        feed_type = choice([
            'breast milk',      # חלב אם
            'formula',          # תרכובת
            'formula',          # תרכובת (סיכוי גבוה יותר)
        ])

        notes = ""
        if choice([True, False, False, False, False]):  # 20% סיכוי להערות
            notes_options = [
                "אכלה טוב! 😊",
                "קצת התפרקנה באמצע",
                "גיהקה הרבה",
                "שתתה הכל!",
                "השאירה קצת בבקבוק",
                "",
            ]
            notes = choice(notes_options)

        if end < self.time_now:
            instance = models.Feeding.objects.create(
                child=self.child,
                start=start,
                end=end,
                type=feed_type,
                method='bottle',  # תמיד בקבוק!
                amount=amount,
                notes=notes,
            )
            instance.save()

        self.time = end

    @transaction.atomic
    def _add_diaperchange_entry(self):
        """
        מוסיף החלפת חיתול
        Add a diaper change entry
        """
        solid = choice([True, False, False, False])  # 25% סיכוי למוצק
        wet = choice([True, True, True, False])     # 75% סיכוי לרטוב

        color = ""
        if solid:
            color = choice(['yellow', 'brown', 'green'])

        amount = Decimal("%d.%d" % (randint(1, 3), randint(0, 9)))
        time = self.time + timedelta(minutes=randint(10, 45))

        notes = ""
        if choice([True, False, False, False, False]):  # 20% סיכוי להערות
            notes_options = [
                "חיתול מלא",
                "החליפו מהר",
                "",
            ]
            notes = choice(notes_options)

        if time < self.time_now:
            instance = models.DiaperChange.objects.create(
                child=self.child,
                time=time,
                wet=wet,
                solid=solid,
                color=color,
                amount=amount,
                notes=notes,
            )
            instance.save()

        self.time = time

    @transaction.atomic
    def _add_sleep_entry(self):
        """
        מוסיף תקופת שינה
        Add a sleep entry

        בלילה (18:00-06:00): 2-6 שעות
        ביום (06:00-18:00): 30 דקות - 2 שעות
        """
        hour = self.time.hour

        # בלילה - שינה ארוכה יותר
        if hour < 6 or hour >= 20:
            minutes = randint(90, 240)  # 1.5-4 שעות
        # בבוקר/אחה"צ - תנומות
        else:
            minutes = randint(30, 120)  # 30 דקות - 2 שעות

        end = self.time + timedelta(minutes=minutes)

        notes = ""
        if choice([True, False, False, False, False]):  # 20% סיכוי להערות
            notes_options = [
                "ישנה טוב",
                "התעוררה באמצע",
                "נרדמה מהר",
                "",
            ]
            notes = choice(notes_options)

        if end < self.time_now:
            instance = models.Sleep.objects.create(
                child=self.child,
                start=self.time,
                end=end,
                notes=notes
            )
            instance.save()

        self.time = end
