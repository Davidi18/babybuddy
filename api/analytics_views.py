# -*- coding: utf-8 -*-
"""
API Views לאנליטיקה וסטטיסטיקות
Analytics and statistics API views
"""
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import views, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core import models
from core.analytics import BabyAnalytics


class ChildAnalyticsView(views.APIView):
    """
    API endpoint לקבלת סטטיסטיקות על ילד ספציפי
    API endpoint for child-specific analytics

    GET /api/analytics/child/<child_slug>/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, child_slug):
        """מחזיר סטטיסטיקות כלליות על הילד"""
        child = get_object_or_404(models.Child, slug=child_slug)
        analytics = BabyAnalytics(child)

        days = int(request.query_params.get("days", 7))

        data = {
            "child": {
                "name": child.name(),
                "slug": child.slug,
                "birth_date": child.birth_date,
            },
            "feeding_stats": analytics.get_feeding_stats(days=days),
            "sleep_stats": analytics.get_sleep_stats(days=days),
            "diaper_stats": analytics.get_diaper_stats(days=days),
        }

        return Response(data)


class ChildCurrentStatusView(views.APIView):
    """
    מצב נוכחי של הילד - מה קרה לאחרונה ומה צפוי
    Current status - what happened recently and what's expected

    GET /api/analytics/child/<child_slug>/status/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, child_slug):
        """מחזיר מצב נוכחי מפורט"""
        child = get_object_or_404(models.Child, slug=child_slug)
        analytics = BabyAnalytics(child)

        status_data = analytics.get_current_status()

        # המרה לפורמט JSON-friendly
        response_data = {
            "child": {
                "name": child.name(),
                "slug": child.slug,
            },
            "timestamp": timezone.now().isoformat(),
            "last_feeding": self._format_last_feeding(status_data["last_feeding"]),
            "next_feeding_prediction": status_data["next_feeding_prediction"],
            "last_sleep": self._format_last_sleep(status_data["last_sleep"]),
            "next_sleep_prediction": status_data["next_sleep_prediction"],
            "last_diaper": self._format_last_diaper(status_data["last_diaper"]),
            "stats_7_days": status_data["stats_7_days"],
        }

        return Response(response_data)

    def _format_last_feeding(self, feeding_info):
        """המרה לפורמט JSON"""
        if not feeding_info:
            return None

        return {
            "time_since_minutes": feeding_info["time_since_minutes"],
            "time_since_hours": feeding_info["time_since_hours"],
            "time_since_formatted": feeding_info["time_since_formatted"],
            "type": feeding_info["type"],
            "amount": feeding_info["amount"],
            "end_time": feeding_info["feeding"].end.isoformat(),
        }

    def _format_last_sleep(self, sleep_info):
        """המרה לפורמט JSON"""
        if not sleep_info:
            return None

        return {
            "time_since_minutes": sleep_info["time_since_minutes"],
            "time_since_hours": sleep_info["time_since_hours"],
            "time_since_formatted": sleep_info["time_since_formatted"],
            "was_nap": sleep_info["was_nap"],
            "duration_minutes": sleep_info["duration_minutes"],
            "end_time": sleep_info["sleep"].end.isoformat(),
        }

    def _format_last_diaper(self, diaper_info):
        """המרה לפורמט JSON"""
        if not diaper_info:
            return None

        return {
            "time_since_minutes": diaper_info["time_since_minutes"],
            "time_since_hours": diaper_info["time_since_hours"],
            "time_since_formatted": diaper_info["time_since_formatted"],
            "was_wet": diaper_info["was_wet"],
            "was_solid": diaper_info["was_solid"],
            "time": diaper_info["change"].time.isoformat(),
        }


class ChildDailySummaryView(views.APIView):
    """
    סיכום יומי של פעילויות הילד
    Daily summary of child activities

    GET /api/analytics/child/<child_slug>/daily/
    GET /api/analytics/child/<child_slug>/daily/?date=2025-01-15
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, child_slug):
        """מחזיר סיכום יומי"""
        child = get_object_or_404(models.Child, slug=child_slug)
        analytics = BabyAnalytics(child)

        # פרסור תאריך
        date_str = request.query_params.get("date")
        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            date = timezone.localdate()

        summary = analytics.get_daily_summary(date)

        response_data = {
            "child": {
                "name": child.name(),
                "slug": child.slug,
            },
            "summary": summary,
        }

        return Response(response_data)


class ChildFeedingPredictionView(views.APIView):
    """
    חיזוי האכלה הבאה
    Next feeding prediction

    GET /api/analytics/child/<child_slug>/predict-feeding/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, child_slug):
        """מחזיר חיזוי להאכלה הבאה"""
        child = get_object_or_404(models.Child, slug=child_slug)
        analytics = BabyAnalytics(child)

        prediction = analytics.predict_next_feeding()

        if not prediction:
            return Response(
                {
                    "error": "Not enough data to predict",
                    "message": "נדרשות לפחות 2 האכלות ב-7 ימים האחרונים",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # המרה לפורמט JSON-friendly
        prediction["estimated_time"] = prediction["estimated_time"].isoformat()

        response_data = {
            "child": {
                "name": child.name(),
                "slug": child.slug,
            },
            "prediction": prediction,
        }

        return Response(response_data)


class ChildSleepPredictionView(views.APIView):
    """
    חיזוי שינה הבאה
    Next sleep prediction

    GET /api/analytics/child/<child_slug>/predict-sleep/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, child_slug):
        """מחזיר חיזוי לשינה הבאה"""
        child = get_object_or_404(models.Child, slug=child_slug)
        analytics = BabyAnalytics(child)

        prediction = analytics.predict_next_sleep()

        if not prediction:
            return Response(
                {
                    "error": "Not enough data to predict",
                    "message": "אין רישום שינה אחרון",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        response_data = {
            "child": {
                "name": child.name(),
                "slug": child.slug,
            },
            "prediction": prediction,
        }

        return Response(response_data)


class AllChildrenStatusView(views.APIView):
    """
    מצב כל הילדים במערכת
    Status of all children in the system

    GET /api/analytics/all-children/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """מחזיר מצב של כל הילדים"""
        children = models.Child.objects.all()

        children_data = []
        for child in children:
            analytics = BabyAnalytics(child)

            last_feeding = analytics.get_last_feeding_info()
            last_sleep = analytics.get_last_sleep_info()
            next_feeding = analytics.predict_next_feeding()

            children_data.append(
                {
                    "name": child.name(),
                    "slug": child.slug,
                    "last_feeding_minutes_ago": (
                        last_feeding["time_since_minutes"] if last_feeding else None
                    ),
                    "last_sleep_minutes_ago": (
                        last_sleep["time_since_minutes"] if last_sleep else None
                    ),
                    "next_feeding_status": (
                        next_feeding["status"] if next_feeding else None
                    ),
                    "next_feeding_message": (
                        next_feeding["message"] if next_feeding else None
                    ),
                }
            )

        return Response({"children": children_data, "count": len(children_data)})
