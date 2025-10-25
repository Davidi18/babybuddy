# -*- coding: utf-8 -*-
"""
Management command להצגת מצב נוכחי של התינוק
Current baby status management command
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Child
from core.analytics import BabyAnalytics


class Command(BaseCommand):
    help = 'הצג מצב נוכחי של התינוק - מה קרה לאחרונה ומה צפוי / Show current baby status'

    def add_arguments(self, parser):
        parser.add_argument(
            '--child',
            type=str,
            help='שם או slug של הילד / Child name or slug',
        )

    def handle(self, *args, **options):
        child_identifier = options.get('child')

        # בחירת ילד
        if child_identifier:
            try:
                child = Child.objects.get(slug=child_identifier)
            except Child.DoesNotExist:
                child = Child.objects.filter(
                    first_name__icontains=child_identifier
                ).first()
                if not child:
                    self.stdout.write(
                        self.style.ERROR(f'❌ לא נמצא ילד: {child_identifier}')
                    )
                    return
        else:
            child = Child.objects.first()
            if not child:
                self.stdout.write(self.style.ERROR('❌ אין ילדים במערכת'))
                return

        analytics = BabyAnalytics(child)
        status = analytics.get_current_status()

        # כותרת
        self.stdout.write('=' * 70)
        self.stdout.write(
            self.style.SUCCESS(
                f'👶 מצב נוכחי של {child.name()} | Current Status of {child.name()}'
            )
        )
        self.stdout.write(f'🕐 {timezone.now().strftime("%A, %d %B %Y - %H:%M")}')
        self.stdout.write('=' * 70)

        # האכלה אחרונה
        last_feeding = status['last_feeding']
        if last_feeding:
            self.stdout.write(f'\n🍼 האכלה אחרונה / Last Feeding:')
            self.stdout.write(f'   ⏱️  לפני {last_feeding["time_since_formatted"]} שעות')
            self.stdout.write(f'   📋 סוג: {last_feeding["type"]}')
            if last_feeding['amount']:
                self.stdout.write(f'   💧 כמות: {last_feeding["amount"]} ml')
        else:
            self.stdout.write(f'\n🍼 אין רישום של האכלה')

        # חיזוי האכלה הבאה
        next_feeding = status['next_feeding_prediction']
        if next_feeding:
            self.stdout.write(f'\n🔮 האכלה הבאה / Next Feeding Prediction:')

            if next_feeding['status'] == 'overdue':
                self.stdout.write(
                    self.style.ERROR(f'   ⚠️  {next_feeding["message"]}')
                )
            elif next_feeding['status'] == 'soon':
                self.stdout.write(
                    self.style.WARNING(f'   ⏰ {next_feeding["message"]}')
                )
            else:
                self.stdout.write(f'   ✓ {next_feeding["message"]}')

            self.stdout.write(
                f'   🕐 זמן משוער: {next_feeding["estimated_time"].strftime("%H:%M")}'
            )

        # שינה אחרונה
        self.stdout.write('\n' + '-' * 70)
        last_sleep = status['last_sleep']
        if last_sleep:
            self.stdout.write(f'\n💤 שינה אחרונה / Last Sleep:')
            self.stdout.write(f'   ⏱️  התעורר לפני {last_sleep["time_since_formatted"]} שעות')
            self.stdout.write(
                f'   ⌛ משך: {last_sleep["duration_minutes"]:.0f} דקות'
            )
            self.stdout.write(
                f'   🌙 סוג: {"תנומה / Nap" if last_sleep["was_nap"] else "שינת לילה / Night sleep"}'
            )
        else:
            self.stdout.write(f'\n💤 אין רישום של שינה')

        # חיזוי שינה הבאה
        next_sleep = status['next_sleep_prediction']
        if next_sleep:
            self.stdout.write(f'\n🔮 שינה הבאה / Next Sleep Prediction:')
            self.stdout.write(f'   ⏰ ער כבר {next_sleep["minutes_awake"]:.0f} דקות')

            if next_sleep['status'] == 'overtired':
                self.stdout.write(
                    self.style.ERROR(f'   ⚠️  {next_sleep["message"]}')
                )
            elif next_sleep['status'] in ['getting_tired', 'soon']:
                self.stdout.write(
                    self.style.WARNING(f'   😴 {next_sleep["message"]}')
                )
            else:
                self.stdout.write(f'   ✓ {next_sleep["message"]}')

        # חיתול אחרון
        self.stdout.write('\n' + '-' * 70)
        last_diaper = status['last_diaper']
        if last_diaper:
            self.stdout.write(f'\n🧷 חיתול אחרון / Last Diaper Change:')
            self.stdout.write(f'   ⏱️  לפני {last_diaper["time_since_formatted"]} שעות')

            attributes = []
            if last_diaper['was_wet']:
                attributes.append('רטוב / Wet')
            if last_diaper['was_solid']:
                attributes.append('מוצק / Solid')

            if attributes:
                self.stdout.write(f'   📋 {", ".join(attributes)}')

            # התראה אם עבר זמן רב
            if last_diaper['time_since_hours'] > 3:
                self.stdout.write(
                    self.style.WARNING(
                        f'   ⚠️  שים לב: עברו יותר מ-3 שעות מאז החיתול האחרון'
                    )
                )
        else:
            self.stdout.write(f'\n🧷 אין רישום של חיתול')

        # סטטיסטיקות שבועיות
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('📊 סטטיסטיקות 7 ימים אחרונים / Last 7 Days Stats')
        self.stdout.write('=' * 70)

        stats = status['stats_7_days']

        # האכלות
        feeding_stats = stats['feeding']
        self.stdout.write(f'\n🍼 האכלות:')
        self.stdout.write(f'   • {feeding_stats["count"]} האכלות')
        self.stdout.write(
            f'   • ממוצע בין האכלות: {feeding_stats["average_interval_minutes"]:.0f} דקות'
        )
        self.stdout.write(
            f'   • ממוצע משך האכלה: {feeding_stats["average_duration_minutes"]:.0f} דקות'
        )

        # שינה
        sleep_stats = stats['sleep']
        self.stdout.write(f'\n💤 שינה:')
        self.stdout.write(
            f'   • ממוצע {sleep_stats["average_sleep_hours_per_day"]:.1f} שעות ביום'
        )
        self.stdout.write(f'   • {sleep_stats["naps_count"]} תנומות')
        self.stdout.write(
            f'   • ממוצע תנומה: {sleep_stats["average_nap_duration_minutes"]:.0f} דקות'
        )

        # חיתולים
        diaper_stats = stats['diapers']
        self.stdout.write(f'\n🧷 חיתולים:')
        self.stdout.write(f'   • {diaper_stats["count"]} חיתולים')
        self.stdout.write(f'   • ממוצע: {diaper_stats["average_per_day"]:.1f} ביום')

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ סיכום מצב הושלם / Status summary completed'))
        self.stdout.write('=' * 70 + '\n')
