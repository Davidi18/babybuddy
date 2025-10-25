# -*- coding: utf-8 -*-
"""
פונקציות אנליטיקה וחיזוי עבור Baby Buddy
Analytics and prediction functions for tracking baby patterns
"""
import datetime
from datetime import timedelta
from typing import Dict, List, Optional, Tuple

from django.db.models import Avg, Count, Sum, QuerySet
from django.utils import timezone


class BabyAnalytics:
    """
    מחלקה לניתוח נתונים וחיזוי דפוסים של התינוק
    Class for analyzing baby data and predicting patterns
    """

    def __init__(self, child):
        """
        :param child: Child model instance
        """
        self.child = child

    # ==================== Feeding Analytics ====================

    def get_feeding_stats(self, days: int = 7) -> Dict:
        """
        מחזיר סטטיסטיקות על האכלות בימים האחרונים
        Returns feeding statistics for the last N days
        """
        from core.models import Feeding

        cutoff = timezone.now() - timedelta(days=days)
        feedings = Feeding.objects.filter(
            child=self.child, start__gte=cutoff
        ).order_by("start")

        if not feedings.exists():
            return {
                "count": 0,
                "average_duration_minutes": 0,
                "average_interval_minutes": 0,
                "total_amount": 0,
                "by_type": {},
            }

        # חישוב ממוצעים
        stats = feedings.aggregate(
            avg_duration=Avg("duration"), total_amount=Sum("amount"), count=Count("id")
        )

        # חישוב מרווח ממוצע בין האכלות
        intervals = []
        feeding_list = list(feedings)
        for i in range(len(feeding_list) - 1):
            interval = feeding_list[i + 1].start - feeding_list[i].end
            intervals.append(interval.total_seconds() / 60)  # המרה לדקות

        avg_interval = sum(intervals) / len(intervals) if intervals else 0

        # ספירה לפי סוג
        by_type = {}
        for feeding in feedings:
            type_name = feeding.type
            by_type[type_name] = by_type.get(type_name, 0) + 1

        return {
            "count": stats["count"],
            "average_duration_minutes": (
                stats["avg_duration"].total_seconds() / 60
                if stats["avg_duration"]
                else 0
            ),
            "average_interval_minutes": round(avg_interval, 1),
            "total_amount": stats["total_amount"] or 0,
            "by_type": by_type,
            "period_days": days,
        }

    def get_last_feeding_info(self) -> Optional[Dict]:
        """
        מחזיר מידע על האכלה אחרונה וכמה זמן עבר מאז
        Returns info about last feeding and time elapsed
        """
        from core.models import Feeding

        last_feeding = (
            Feeding.objects.filter(child=self.child).order_by("-end").first()
        )

        if not last_feeding:
            return None

        time_since = timezone.now() - last_feeding.end
        hours = time_since.total_seconds() / 3600
        minutes = (time_since.total_seconds() % 3600) / 60

        return {
            "feeding": last_feeding,
            "time_since_minutes": time_since.total_seconds() / 60,
            "time_since_hours": hours,
            "time_since_formatted": f"{int(hours)}:{int(minutes):02d}",
            "type": last_feeding.type,
            "amount": last_feeding.amount,
        }

    def predict_next_feeding(self) -> Optional[Dict]:
        """
        מנבא מתי תהיה ההאכלה הבאה בהתבסס על דפוסים
        Predicts when the next feeding will be based on patterns
        """
        stats = self.get_feeding_stats(days=7)
        last_feeding = self.get_last_feeding_info()

        if not last_feeding or stats["count"] < 2:
            return None

        avg_interval_minutes = stats["average_interval_minutes"]
        time_since_minutes = last_feeding["time_since_minutes"]

        # חישוב זמן משוער להאכלה הבאה
        minutes_until_next = avg_interval_minutes - time_since_minutes

        if minutes_until_next < 0:
            # עבר הזמן הממוצע - התינוק כנראה רעב!
            status = "overdue"
            minutes_until_next = abs(minutes_until_next)
            message = f"עבר הזמן! התינוק כנראה רעב (איחור של {int(minutes_until_next)} דקות)"
        elif minutes_until_next < 30:
            status = "soon"
            message = f"בקרוב! בעוד ~{int(minutes_until_next)} דקות"
        elif minutes_until_next < 60:
            status = "upcoming"
            message = f"בעוד ~{int(minutes_until_next)} דקות"
        else:
            status = "later"
            hours = minutes_until_next / 60
            message = f"בעוד ~{hours:.1f} שעות"

        next_feeding_time = timezone.now() + timedelta(minutes=minutes_until_next)

        return {
            "status": status,
            "message": message,
            "minutes_until_next": round(minutes_until_next, 1),
            "estimated_time": next_feeding_time,
            "average_interval_minutes": avg_interval_minutes,
            "confidence": "high" if stats["count"] >= 10 else "medium",
        }

    # ==================== Sleep Analytics ====================

    def get_sleep_stats(self, days: int = 7) -> Dict:
        """
        מחזיר סטטיסטיקות על שינה בימים האחרונים
        Returns sleep statistics for the last N days
        """
        from core.models import Sleep

        cutoff = timezone.now() - timedelta(days=days)
        sleep_entries = Sleep.objects.filter(
            child=self.child, start__gte=cutoff
        ).order_by("start")

        if not sleep_entries.exists():
            return {
                "count": 0,
                "total_sleep_hours": 0,
                "average_sleep_hours_per_day": 0,
                "naps_count": 0,
                "night_sleep_count": 0,
                "average_nap_duration_minutes": 0,
            }

        stats = sleep_entries.aggregate(
            avg_duration=Avg("duration"),
            total_duration=Sum("duration"),
            count=Count("id"),
        )

        naps = sleep_entries.filter(nap=True)
        night_sleep = sleep_entries.filter(nap=False)

        total_hours = (
            stats["total_duration"].total_seconds() / 3600
            if stats["total_duration"]
            else 0
        )
        avg_hours_per_day = total_hours / days if days > 0 else 0

        nap_avg = naps.aggregate(avg_duration=Avg("duration"))
        nap_avg_minutes = (
            nap_avg["avg_duration"].total_seconds() / 60
            if nap_avg["avg_duration"]
            else 0
        )

        return {
            "count": stats["count"],
            "total_sleep_hours": round(total_hours, 1),
            "average_sleep_hours_per_day": round(avg_hours_per_day, 1),
            "naps_count": naps.count(),
            "night_sleep_count": night_sleep.count(),
            "average_nap_duration_minutes": round(nap_avg_minutes, 1),
            "period_days": days,
        }

    def get_last_sleep_info(self) -> Optional[Dict]:
        """
        מחזיר מידע על שינה אחרונה
        Returns info about last sleep
        """
        from core.models import Sleep

        last_sleep = Sleep.objects.filter(child=self.child).order_by("-end").first()

        if not last_sleep:
            return None

        time_since = timezone.now() - last_sleep.end
        hours = time_since.total_seconds() / 3600
        minutes = (time_since.total_seconds() % 3600) / 60

        sleep_duration_minutes = last_sleep.duration.total_seconds() / 60

        return {
            "sleep": last_sleep,
            "time_since_minutes": time_since.total_seconds() / 60,
            "time_since_hours": hours,
            "time_since_formatted": f"{int(hours)}:{int(minutes):02d}",
            "was_nap": last_sleep.nap,
            "duration_minutes": sleep_duration_minutes,
        }

    def predict_next_sleep(self) -> Optional[Dict]:
        """
        מנבא מתי תהיה השינה הבאה
        Predicts when the next sleep will be
        """
        last_sleep = self.get_last_sleep_info()

        if not last_sleep:
            return None

        time_awake_minutes = last_sleep["time_since_minutes"]

        # כללי אצבע לפי גיל (זה פשוט - אפשר לשפר)
        # יילוד: ערים 45-60 דקות
        # 3-6 חודשים: ערים 1.5-2 שעות
        # 6-12 חודשים: ערים 2-3 שעות

        # נניח 90 דקות כברירת מחדל (אפשר לשפר עם גיל התינוק)
        typical_wake_window = 90

        minutes_until_tired = typical_wake_window - time_awake_minutes

        if minutes_until_tired < 0:
            status = "overtired"
            message = f"התינוק כנראה עייף! עבר הזמן ב-{int(abs(minutes_until_tired))} דקות"
        elif minutes_until_tired < 15:
            status = "getting_tired"
            message = f"התינוק מתחיל להתעייף - בעוד ~{int(minutes_until_tired)} דקות"
        elif minutes_until_tired < 30:
            status = "soon"
            message = f"בקרוב יתעייף - בעוד ~{int(minutes_until_tired)} דקות"
        else:
            status = "awake"
            message = f"עוד {int(minutes_until_tired)} דקות עד שיתעייף"

        return {
            "status": status,
            "message": message,
            "minutes_awake": round(time_awake_minutes, 1),
            "minutes_until_tired": round(minutes_until_tired, 1),
            "typical_wake_window_minutes": typical_wake_window,
        }

    # ==================== Diaper Change Analytics ====================

    def get_diaper_stats(self, days: int = 7) -> Dict:
        """
        מחזיר סטטיסטיקות על חיתולים
        Returns diaper change statistics
        """
        from core.models import DiaperChange

        cutoff = timezone.now() - timedelta(days=days)
        changes = DiaperChange.objects.filter(child=self.child, time__gte=cutoff)

        if not changes.exists():
            return {
                "count": 0,
                "wet_count": 0,
                "solid_count": 0,
                "average_per_day": 0,
            }

        wet_count = changes.filter(wet=True).count()
        solid_count = changes.filter(solid=True).count()

        return {
            "count": changes.count(),
            "wet_count": wet_count,
            "solid_count": solid_count,
            "average_per_day": round(changes.count() / days, 1),
            "period_days": days,
        }

    def get_last_diaper_info(self) -> Optional[Dict]:
        """
        מחזיר מידע על חיתול אחרון
        Returns info about last diaper change
        """
        from core.models import DiaperChange

        last_change = (
            DiaperChange.objects.filter(child=self.child).order_by("-time").first()
        )

        if not last_change:
            return None

        time_since = timezone.now() - last_change.time
        hours = time_since.total_seconds() / 3600
        minutes = (time_since.total_seconds() % 3600) / 60

        return {
            "change": last_change,
            "time_since_minutes": time_since.total_seconds() / 60,
            "time_since_hours": hours,
            "time_since_formatted": f"{int(hours)}:{int(minutes):02d}",
            "was_wet": last_change.wet,
            "was_solid": last_change.solid,
        }

    # ==================== Combined Analytics ====================

    def get_daily_summary(self, date: Optional[datetime.date] = None) -> Dict:
        """
        מחזיר סיכום יומי של כל הפעילויות
        Returns daily summary of all activities
        """
        from core.models import Feeding, Sleep, DiaperChange

        if date is None:
            date = timezone.localdate()

        start_of_day = timezone.make_aware(
            datetime.datetime.combine(date, datetime.time.min)
        )
        end_of_day = timezone.make_aware(
            datetime.datetime.combine(date, datetime.time.max)
        )

        # Feedings
        feedings = Feeding.objects.filter(
            child=self.child, start__gte=start_of_day, start__lte=end_of_day
        )

        # Sleep
        sleep_entries = Sleep.objects.filter(
            child=self.child, start__gte=start_of_day, start__lte=end_of_day
        )

        # Diaper changes
        diaper_changes = DiaperChange.objects.filter(
            child=self.child, time__gte=start_of_day, time__lte=end_of_day
        )

        # חישובים
        total_feeding_duration = sum(
            [f.duration.total_seconds() / 60 for f in feedings if f.duration], 0
        )
        total_sleep_duration = sum(
            [s.duration.total_seconds() / 60 for s in sleep_entries if s.duration], 0
        )
        total_feeding_amount = sum([f.amount for f in feedings if f.amount], 0)

        return {
            "date": date.isoformat(),
            "feedings": {
                "count": feedings.count(),
                "total_duration_minutes": round(total_feeding_duration, 1),
                "total_amount": total_feeding_amount,
            },
            "sleep": {
                "count": sleep_entries.count(),
                "total_duration_minutes": round(total_sleep_duration, 1),
                "total_duration_hours": round(total_sleep_duration / 60, 1),
                "naps": sleep_entries.filter(nap=True).count(),
            },
            "diapers": {
                "count": diaper_changes.count(),
                "wet": diaper_changes.filter(wet=True).count(),
                "solid": diaper_changes.filter(solid=True).count(),
            },
        }

    def get_current_status(self) -> Dict:
        """
        מחזיר את המצב הנוכחי - מה קרה לאחרונה ומה צפוי להיות בקרוב
        Returns current status - what happened recently and what's coming
        """
        return {
            "last_feeding": self.get_last_feeding_info(),
            "next_feeding_prediction": self.predict_next_feeding(),
            "last_sleep": self.get_last_sleep_info(),
            "next_sleep_prediction": self.predict_next_sleep(),
            "last_diaper": self.get_last_diaper_info(),
            "stats_7_days": {
                "feeding": self.get_feeding_stats(days=7),
                "sleep": self.get_sleep_stats(days=7),
                "diapers": self.get_diaper_stats(days=7),
            },
        }
