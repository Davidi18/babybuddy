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

from api.llm_messages import format_time_since


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
            "time_since_formatted": format_time_since(hours),
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
            # עבר הזמן הממוצע - התינוקת כנראה רעבה!
            status = "overdue"
            minutes_until_next = abs(minutes_until_next)
            message = f"{self.child.first_name} כנראה רעבה (לפני {int(minutes_until_next)} דקות)"
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
            "time_since_formatted": format_time_since(hours),
            "was_nap": last_sleep.nap,
            "duration_minutes": sleep_duration_minutes,
        }

    def _get_age_based_wake_window(self) -> Tuple[float, float]:
        """
        מחזיר חלון ערות מומלץ לפי גיל התינוק (דקות).
        Returns recommended wake window range (min, max) in minutes based on age.
        מבוסס על המלצות רפואיות מקובלות.
        """
        if not self.child.birth_date:
            return (60.0, 120.0)

        today = timezone.localdate()
        age_days = (today - self.child.birth_date).days
        age_months = age_days / 30.44  # ממוצע ימים בחודש

        if age_months < 1:
            return (35.0, 60.0)       # יילוד: 35-60 דקות
        elif age_months < 2:
            return (45.0, 75.0)       # חודש-חודשיים: 45-75 דקות
        elif age_months < 3:
            return (60.0, 90.0)       # 2-3 חודשים: 60-90 דקות
        elif age_months < 4:
            return (75.0, 120.0)      # 3-4 חודשים: 75-120 דקות
        elif age_months < 6:
            return (90.0, 150.0)      # 4-6 חודשים: 1.5-2.5 שעות
        elif age_months < 9:
            return (120.0, 180.0)     # 6-9 חודשים: 2-3 שעות
        elif age_months < 12:
            return (150.0, 240.0)     # 9-12 חודשים: 2.5-4 שעות
        elif age_months < 18:
            return (180.0, 300.0)     # 12-18 חודשים: 3-5 שעות
        else:
            return (240.0, 360.0)     # 18+ חודשים: 4-6 שעות

    def _calculate_wake_windows(self, days: int = 14) -> List[Dict]:
        """
        מחשב את חלונות הערות בפועל מנתוני השינה.
        Calculates actual wake windows from sleep data.

        חלון ערות = הזמן מסוף שינה אחת עד תחילת השינה הבאה.
        Wake window = time from end of one sleep to start of next sleep.
        """
        from core.models import Sleep

        cutoff = timezone.now() - timedelta(days=days)
        sleep_entries = list(
            Sleep.objects.filter(child=self.child, start__gte=cutoff)
            .order_by("start")
        )

        if len(sleep_entries) < 2:
            return []

        wake_windows = []
        for i in range(len(sleep_entries) - 1):
            current_end = sleep_entries[i].end
            next_start = sleep_entries[i + 1].start

            wake_minutes = (next_start - current_end).total_seconds() / 60

            # מסנן ערכים לא הגיוניים (למשל חפיפות או פערים מעל 12 שעות)
            if wake_minutes < 5 or wake_minutes > 720:
                continue

            local_end = timezone.localtime(current_end)
            hour_of_day = local_end.hour

            wake_windows.append({
                "wake_minutes": wake_minutes,
                "hour_of_day": hour_of_day,
                "date": local_end.date(),
                "was_nap": sleep_entries[i].nap,
                "next_was_nap": sleep_entries[i + 1].nap,
                "sleep_duration_minutes": (
                    sleep_entries[i].duration.total_seconds() / 60
                    if sleep_entries[i].duration
                    else 0
                ),
            })

        return wake_windows

    def _weighted_average_wake_window(
        self, wake_windows: List[Dict], current_hour: Optional[int] = None
    ) -> float:
        """
        ממוצע משוקלל של חלונות ערות.
        Weighted average of wake windows with recency bias and time-of-day matching.

        חלונות אחרונים מקבלים משקל גבוה יותר (דעיכה אקספוננציאלית).
        חלונות בשעה דומה ביום מקבלים בונוס.
        """
        if not wake_windows:
            return 0

        now = timezone.localdate()
        total_weight = 0.0
        weighted_sum = 0.0

        for ww in wake_windows:
            # משקל לפי עדכניות (דעיכה אקספוננציאלית)
            days_ago = (now - ww["date"]).days
            recency_weight = 0.9 ** days_ago  # כל יום שעובר = 10% פחות משקל

            # בונוס לשעה דומה ביום (±2 שעות)
            time_weight = 1.0
            if current_hour is not None:
                hour_diff = abs(ww["hour_of_day"] - current_hour)
                if hour_diff > 12:
                    hour_diff = 24 - hour_diff
                if hour_diff <= 2:
                    time_weight = 1.5  # 50% בונוס לשעה דומה
                elif hour_diff <= 4:
                    time_weight = 1.2  # 20% בונוס לשעה קרובה

            weight = recency_weight * time_weight
            weighted_sum += ww["wake_minutes"] * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0

    def predict_next_sleep(self) -> Optional[Dict]:
        """
        אלגוריתם חכם לחיזוי שינה - לומד מנתוני השינה בפועל.
        Smart sleep prediction algorithm - learns from actual sleep data.

        שלב 1: מחשב חלונות ערות מנתונים היסטוריים (14 ימים)
        שלב 2: ממוצע משוקלל עם דגש על ימים אחרונים ושעת היום
        שלב 3: משלב עם טווח מומלץ לפי גיל כ-fallback
        שלב 4: מחזיר חיזוי עם רמת ביטחון
        """
        last_sleep = self.get_last_sleep_info()

        if not last_sleep:
            return None

        time_awake_minutes = last_sleep["time_since_minutes"]
        current_hour = timezone.localtime().hour

        # שלב 1: חלונות ערות מהנתונים
        wake_windows = self._calculate_wake_windows(days=14)

        # שלב 2: חלון ערות לפי גיל (כ-fallback)
        age_min, age_max = self._get_age_based_wake_window()
        age_midpoint = (age_min + age_max) / 2

        # שלב 3: חישוב חלון ערות חזוי
        if len(wake_windows) >= 5:
            # מספיק נתונים - נשתמש בממוצע משוקלל
            data_wake_window = self._weighted_average_wake_window(
                wake_windows, current_hour
            )
            # משלב 70% נתונים + 30% גיל (כדי למנוע חריגות קיצוניות)
            predicted_wake_window = (data_wake_window * 0.7) + (age_midpoint * 0.3)
            # מגביל לטווח הגיוני (±50% מטווח הגיל)
            predicted_wake_window = max(
                age_min * 0.5, min(age_max * 1.5, predicted_wake_window)
            )
            confidence = "high"
            data_source = "learned"
        elif len(wake_windows) >= 2:
            # מעט נתונים - שילוב שווה
            data_wake_window = self._weighted_average_wake_window(
                wake_windows, current_hour
            )
            predicted_wake_window = (data_wake_window * 0.4) + (age_midpoint * 0.6)
            predicted_wake_window = max(
                age_min * 0.7, min(age_max * 1.3, predicted_wake_window)
            )
            confidence = "medium"
            data_source = "mixed"
        else:
            # אין מספיק נתונים - נשתמש בהמלצה לפי גיל
            predicted_wake_window = age_midpoint
            confidence = "low"
            data_source = "age_based"

        minutes_until_tired = predicted_wake_window - time_awake_minutes

        # שלב 4: סטטוס והודעה
        if minutes_until_tired < -15:
            status = "overtired"
            overdue = int(abs(minutes_until_tired))
            message = (
                f"{self.child.first_name} כנראה עייפה מאוד "
                f"(ערה {overdue} דקות יותר מהרגיל)"
            )
        elif minutes_until_tired < 0:
            status = "overtired"
            message = (
                f"{self.child.first_name} כנראה עייפה "
                f"(עבר הזמן הרגיל שלה)"
            )
        elif minutes_until_tired < 15:
            status = "getting_tired"
            message = (
                f"{self.child.first_name} מתחילה להתעייף - "
                f"בעוד ~{int(minutes_until_tired)} דקות"
            )
        elif minutes_until_tired < 30:
            status = "soon"
            message = f"בקרוב תתעייף - בעוד ~{int(minutes_until_tired)} דקות"
        else:
            status = "awake"
            hours = minutes_until_tired / 60
            if hours >= 1:
                h = int(hours)
                m = int(minutes_until_tired % 60)
                message = f"עוד כ-{h}:{m:02d} שעות עד שתתעייף"
            else:
                message = f"עוד ~{int(minutes_until_tired)} דקות עד שתתעייף"

        estimated_sleep_time = timezone.now() + timedelta(minutes=max(0, minutes_until_tired))

        # סטטיסטיקות על חלונות ערות
        ww_stats = {}
        if wake_windows:
            ww_values = [ww["wake_minutes"] for ww in wake_windows]
            ww_stats = {
                "sample_size": len(wake_windows),
                "average_minutes": round(sum(ww_values) / len(ww_values), 1),
                "shortest_minutes": round(min(ww_values), 1),
                "longest_minutes": round(max(ww_values), 1),
            }

        return {
            "status": status,
            "message": message,
            "minutes_awake": round(time_awake_minutes, 1),
            "minutes_until_tired": round(minutes_until_tired, 1),
            "predicted_wake_window_minutes": round(predicted_wake_window, 1),
            "estimated_sleep_time": estimated_sleep_time.isoformat(),
            "confidence": confidence,
            "data_source": data_source,
            "age_recommended_range": {
                "min_minutes": age_min,
                "max_minutes": age_max,
            },
            "wake_window_stats": ww_stats,
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
            "time_since_formatted": format_time_since(hours),
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
