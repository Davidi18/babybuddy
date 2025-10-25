# -*- coding: utf-8 -*-
"""
Management command לסיכום יומי של פעילויות התינוק
Daily summary management command
"""
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Child
from core.analytics import BabyAnalytics


class Command(BaseCommand):
    help = 'הצג סיכום יומי של פעילויות התינוק / Display daily summary of baby activities'

    def add_arguments(self, parser):
        parser.add_argument(
            '--child',
            type=str,
            help='שם או slug של הילד / Child name or slug',
        )
        parser.add_argument(
            '--date',
            type=str,
            help='תאריך (YYYY-MM-DD), ברירת מחדל: היום / Date (YYYY-MM-DD), default: today',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='מספר ימים לסיכום / Number of days to summarize',
        )

    def handle(self, *args, **options):
        child_identifier = options.get('child')
        date_str = options.get('date')
        days = options['days']

        # בחירת ילד
        if child_identifier:
            try:
                child = Child.objects.get(slug=child_identifier)
            except Child.DoesNotExist:
                # נסה לפי שם
                child = Child.objects.filter(first_name__icontains=child_identifier).first()
                if not child:
                    self.stdout.write(
                        self.style.ERROR(f'❌ לא נמצא ילד: {child_identifier}')
                    )
                    return
        else:
            # ברירת מחדל: הילד הראשון
            child = Child.objects.first()
            if not child:
                self.stdout.write(self.style.ERROR('❌ אין ילדים במערכת'))
                return

        # פרסור תאריך
        if date_str:
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('❌ פורמט תאריך שגוי. השתמש ב-YYYY-MM-DD')
                )
                return
        else:
            date = timezone.localdate()

        # כותרת
        self.stdout.write('=' * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 סיכום יומי עבור {child.name()} | Daily Summary for {child.name()}'
            )
        )
        self.stdout.write('=' * 60)

        analytics = BabyAnalytics(child)

        # סיכום לכל יום
        for day_offset in range(days):
            current_date = date - datetime.timedelta(days=day_offset)
            summary = analytics.get_daily_summary(current_date)

            self.stdout.write(f'\n📅 {current_date.strftime("%A, %Y-%m-%d")}')
            self.stdout.write('-' * 60)

            # האכלות
            feeding_data = summary['feedings']
            self.stdout.write(f'\n🍼 האכלות / Feedings:')
            self.stdout.write(f'   • מספר: {feeding_data["count"]}')
            self.stdout.write(
                f'   • משך כולל: {feeding_data["total_duration_minutes"]:.1f} דקות'
            )
            if feeding_data['total_amount']:
                self.stdout.write(f'   • כמות כוללת: {feeding_data["total_amount"]} ml')

            # שינה
            sleep_data = summary['sleep']
            self.stdout.write(f'\n💤 שינה / Sleep:')
            self.stdout.write(f'   • מספר תקופות שינה: {sleep_data["count"]}')
            self.stdout.write(f'   • תנומות: {sleep_data["naps"]}')
            self.stdout.write(
                f'   • שינה כוללת: {sleep_data["total_duration_hours"]:.1f} שעות '
                f'({sleep_data["total_duration_minutes"]:.0f} דקות)'
            )

            # חיתולים
            diaper_data = summary['diapers']
            self.stdout.write(f'\n🧷 חיתולים / Diapers:')
            self.stdout.write(f'   • סה"כ: {diaper_data["count"]}')
            self.stdout.write(f'   • רטובים: {diaper_data["wet"]}')
            self.stdout.write(f'   • מוצקים: {diaper_data["solid"]}')

        # סיכום שבועי
        if days == 1:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.WARNING('📈 סטטיסטיקות 7 ימים אחרונים'))
            self.stdout.write('=' * 60)

            # סטטיסטיקות האכלה
            feeding_stats = analytics.get_feeding_stats(days=7)
            self.stdout.write(f'\n🍼 האכלות:')
            self.stdout.write(f'   • ממוצע בין האכלות: {feeding_stats["average_interval_minutes"]:.1f} דקות')
            self.stdout.write(f'   • ממוצע משך האכלה: {feeding_stats["average_duration_minutes"]:.1f} דקות')
            self.stdout.write(f'   • סה"כ האכלות: {feeding_stats["count"]}')

            # סטטיסטיקות שינה
            sleep_stats = analytics.get_sleep_stats(days=7)
            self.stdout.write(f'\n💤 שינה:')
            self.stdout.write(f'   • ממוצע שעות שינה ביום: {sleep_stats["average_sleep_hours_per_day"]:.1f} שעות')
            self.stdout.write(f'   • ממוצע משך תנומה: {sleep_stats["average_nap_duration_minutes"]:.1f} דקות')
            self.stdout.write(f'   • סה"כ תנומות: {sleep_stats["naps_count"]}')

            # חיזויים
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.WARNING('🔮 חיזויים / Predictions'))
            self.stdout.write('=' * 60)

            # חיזוי האכלה
            next_feeding = analytics.predict_next_feeding()
            if next_feeding:
                self.stdout.write(f'\n🍼 האכלה הבאה:')
                self.stdout.write(f'   {next_feeding["message"]}')
                self.stdout.write(
                    f'   זמן משוער: {next_feeding["estimated_time"].strftime("%H:%M")}'
                )

            # חיזוי שינה
            next_sleep = analytics.predict_next_sleep()
            if next_sleep:
                self.stdout.write(f'\n💤 שינה הבאה:')
                self.stdout.write(f'   {next_sleep["message"]}')

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ סיכום הושלם / Summary completed'))
        self.stdout.write('=' * 60 + '\n')
