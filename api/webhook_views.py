# -*- coding: utf-8 -*-
"""
Webhook Views לשילוב עם אוטומציות חיצוניות (n8n, Zapier, Make, וכו')
Webhook views for external automation integration
"""
import json
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Child
from core.analytics import BabyAnalytics


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def daily_summary_webhook(request):
    """
    Webhook לסיכום יומי - מתאים ל-n8n / Zapier / Make
    Daily summary webhook - suitable for n8n / Zapier / Make

    GET/POST /api/webhooks/daily-summary/
    GET/POST /api/webhooks/daily-summary/?child=emma
    """
    child_slug = request.GET.get('child') or request.POST.get('child')

    # בחירת ילד
    if child_slug:
        try:
            child = Child.objects.get(slug=child_slug)
        except Child.DoesNotExist:
            return Response(
                {'error': f'Child not found: {child_slug}'},
                status=404
            )
    else:
        child = Child.objects.first()
        if not child:
            return Response(
                {'error': 'No children in the system'},
                status=404
            )

    analytics = BabyAnalytics(child)

    # סיכום יומי
    today_summary = analytics.get_daily_summary()

    # מצב נוכחי
    status = analytics.get_current_status()

    # סטטיסטיקות שבועיות
    feeding_stats = analytics.get_feeding_stats(days=7)
    sleep_stats = analytics.get_sleep_stats(days=7)

    # חיזויים
    next_feeding = analytics.predict_next_feeding()
    next_sleep = analytics.predict_next_sleep()

    # בניית הודעה טקסטואלית (לשליחה בהודעות)
    message_parts = [
        f"📊 סיכום יומי - {child.name()}",
        f"📅 {timezone.localdate().strftime('%d/%m/%Y')}",
        "",
        "🍼 האכלות היום:",
        f"  • {today_summary['feedings']['count']} האכלות",
        f"  • {today_summary['feedings']['total_duration_minutes']:.0f} דקות",
    ]

    if today_summary['feedings']['total_amount']:
        message_parts.append(f"  • {today_summary['feedings']['total_amount']:.0f} ml")

    message_parts.extend([
        "",
        "💤 שינה היום:",
        f"  • {today_summary['sleep']['count']} תקופות שינה",
        f"  • {today_summary['sleep']['total_duration_hours']:.1f} שעות",
        f"  • {today_summary['sleep']['naps']} תנומות",
        "",
        "🧷 חיתולים היום:",
        f"  • {today_summary['diapers']['count']} חיתולים",
        "",
        "📈 ממוצעים שבועיים:",
        f"  • האכלה כל {feeding_stats['average_interval_minutes']:.0f} דקות",
        f"  • {sleep_stats['average_sleep_hours_per_day']:.1f} שעות שינה ביום",
    ])

    # הוספת חיזויים
    if next_feeding:
        message_parts.extend([
            "",
            "🔮 חיזויים:",
            f"  • האכלה הבאה: {next_feeding['message']}",
        ])

        if next_feeding['status'] in ['overdue', 'soon']:
            message_parts.append("  ⚠️ שים לב!")

    if next_sleep:
        message_parts.append(f"  • שינה: {next_sleep['message']}")

    message_text = "\n".join(message_parts)

    # Response מובנה ל-n8n
    response_data = {
        'success': True,
        'timestamp': timezone.now().isoformat(),
        'child': {
            'name': child.name(),
            'slug': child.slug,
        },
        'message': message_text,  # טקסט מעוצב לשליחה
        'data': {
            'today': today_summary,
            'stats_7_days': {
                'feeding': feeding_stats,
                'sleep': sleep_stats,
            },
            'predictions': {
                'next_feeding': next_feeding,
                'next_sleep': next_sleep,
            },
        },
        # שדות נוספים שימושיים ל-n8n
        'alerts': [],
    }

    # זיהוי התראות
    if next_feeding and next_feeding['status'] == 'overdue':
        response_data['alerts'].append({
            'type': 'feeding_overdue',
            'severity': 'high',
            'message': next_feeding['message'],
        })

    if next_sleep and next_sleep['status'] == 'overtired':
        response_data['alerts'].append({
            'type': 'overtired',
            'severity': 'medium',
            'message': next_sleep['message'],
        })

    # אם עברו יותר מ-3 שעות מחיתול אחרון
    last_diaper = status.get('last_diaper')
    if last_diaper and last_diaper['time_since_hours'] > 3:
        response_data['alerts'].append({
            'type': 'diaper_overdue',
            'severity': 'medium',
            'message': f'עברו {last_diaper["time_since_hours"]:.1f} שעות מחיתול אחרון',
        })

    return Response(response_data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def status_webhook(request):
    """
    Webhook למצב נוכחי - מתאים לבדיקות תכופות
    Current status webhook - suitable for frequent checks

    GET/POST /api/webhooks/status/
    GET/POST /api/webhooks/status/?child=emma
    """
    child_slug = request.GET.get('child') or request.POST.get('child')

    if child_slug:
        try:
            child = Child.objects.get(slug=child_slug)
        except Child.DoesNotExist:
            return Response({'error': f'Child not found: {child_slug}'}, status=404)
    else:
        child = Child.objects.first()
        if not child:
            return Response({'error': 'No children in the system'}, status=404)

    analytics = BabyAnalytics(child)
    status = analytics.get_current_status()

    # מצב נוכחי בפורמט פשוט
    last_feeding = status.get('last_feeding')
    last_sleep = status.get('last_sleep')
    last_diaper = status.get('last_diaper')
    next_feeding = status.get('next_feeding_prediction')
    next_sleep = status.get('next_sleep_prediction')

    # טקסט סטטוס קצר
    status_parts = [f"👶 {child.name()}"]

    if last_feeding:
        status_parts.append(
            f"🍼 האכלה: לפני {last_feeding['time_since_formatted']}"
        )

    if last_sleep:
        status_parts.append(
            f"💤 ער: {last_sleep['time_since_formatted']}"
        )

    if next_feeding and next_feeding['status'] in ['overdue', 'soon']:
        status_parts.append(f"⚠️ {next_feeding['message']}")

    status_text = " | ".join(status_parts)

    response_data = {
        'success': True,
        'timestamp': timezone.now().isoformat(),
        'child': {
            'name': child.name(),
            'slug': child.slug,
        },
        'status_text': status_text,
        'last_feeding_minutes_ago': (
            last_feeding['time_since_minutes'] if last_feeding else None
        ),
        'last_sleep_minutes_ago': (
            last_sleep['time_since_minutes'] if last_sleep else None
        ),
        'last_diaper_minutes_ago': (
            last_diaper['time_since_minutes'] if last_diaper else None
        ),
        'next_feeding_status': next_feeding['status'] if next_feeding else None,
        'next_feeding_prediction': next_feeding,
        'next_sleep_status': next_sleep['status'] if next_sleep else None,
        'next_sleep_prediction': next_sleep,
        'alerts': [],
    }

    # התראות
    if next_feeding and next_feeding['status'] == 'overdue':
        response_data['alerts'].append({
            'type': 'feeding_overdue',
            'message': next_feeding['message'],
        })

    if next_sleep and next_sleep['status'] == 'overtired':
        response_data['alerts'].append({
            'type': 'overtired',
            'message': next_sleep['message'],
        })

    return Response(response_data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def alerts_webhook(request):
    """
    Webhook להתראות בלבד - מחזיר רק אם יש משהו דחוף
    Alerts-only webhook - returns only if there's something urgent

    GET/POST /api/webhooks/alerts/
    GET/POST /api/webhooks/alerts/?child=emma
    """
    child_slug = request.GET.get('child') or request.POST.get('child')

    if child_slug:
        try:
            child = Child.objects.get(slug=child_slug)
        except Child.DoesNotExist:
            return Response({'error': f'Child not found: {child_slug}'}, status=404)
    else:
        child = Child.objects.first()
        if not child:
            return Response({'error': 'No children in the system'}, status=404)

    analytics = BabyAnalytics(child)
    status = analytics.get_current_status()

    alerts = []

    # בדיקת האכלה
    next_feeding = status.get('next_feeding_prediction')
    if next_feeding and next_feeding['status'] == 'overdue':
        alerts.append({
            'type': 'feeding_overdue',
            'severity': 'high',
            'title': f'{child.first_name} רעבה!',
            'message': next_feeding['message'],
            'minutes_overdue': abs(next_feeding['minutes_until_next']),
        })

    # בדיקת שינה
    next_sleep = status.get('next_sleep_prediction')
    if next_sleep and next_sleep['status'] == 'overtired':
        alerts.append({
            'type': 'overtired',
            'severity': 'high',
            'title': f'{child.first_name} עייפה מאוד!',
            'message': next_sleep['message'],
            'minutes_awake': next_sleep['minutes_awake'],
        })

    # בדיקת חיתול
    last_diaper = status.get('last_diaper')
    if last_diaper and last_diaper['time_since_hours'] > 3:
        alerts.append({
            'type': 'diaper_overdue',
            'severity': 'medium',
            'title': 'זמן לחיתול',
            'message': f'עברו {last_diaper["time_since_hours"]:.1f} שעות מחיתול אחרון',
            'hours_since': last_diaper['time_since_hours'],
        })

    # אם אין התראות
    if not alerts:
        return Response({
            'success': True,
            'has_alerts': False,
            'message': 'הכל בסדר! אין התראות',
            'child': {
                'name': child.name(),
                'slug': child.slug,
            },
        })

    # יש התראות!
    return Response({
        'success': True,
        'has_alerts': True,
        'alert_count': len(alerts),
        'child': {
            'name': child.name(),
            'slug': child.slug,
        },
        'alerts': alerts,
        'timestamp': timezone.now().isoformat(),
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def medication_status_webhook(request):
    """
    Webhook for medication status and reminders

    GET/POST /api/webhooks/medications/
    GET/POST /api/webhooks/medications/?child=emma
    """
    from core.models import Medication, MedicationDose
    from django.db.models import Q

    child_slug = request.GET.get('child') or request.POST.get('child')

    if child_slug:
        try:
            child = Child.objects.get(slug=child_slug)
        except Child.DoesNotExist:
            return Response({'error': f'Child not found: {child_slug}'}, status=404)
    else:
        child = Child.objects.first()
        if not child:
            return Response({'error': 'No children in the system'}, status=404)

    today = timezone.localdate()
    now = timezone.now()

    # Get all active medications
    active_medications = Medication.objects.filter(
        child=child,
        active=True,
        start_date__lte=today
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    )

    medications_due = []
    next_medication = None
    earliest_time = None

    for medication in active_medications:
        if medication.is_due_today():
            next_time = medication.next_dose_time()

            med_info = {
                'id': medication.id,
                'name': medication.name,
                'type': medication.medication_type,
                'dosage': medication.dosage,
                'frequency': medication.frequency,
                'schedule_times': medication.schedule_times,
            }

            if next_time:
                minutes_until = int((next_time - now).total_seconds() / 60)
                med_info['next_dose_time'] = next_time.isoformat()
                med_info['minutes_until'] = minutes_until
                med_info['is_overdue'] = minutes_until < 0

                if not earliest_time or next_time < earliest_time:
                    earliest_time = next_time
                    next_medication = med_info

            medications_due.append(med_info)

    # Build message for WhatsApp/Telegram
    if medications_due:
        message_parts = [
            f"💊 תרופות ל-{child.first_name}",
            f"📅 {today.strftime('%d/%m/%Y')}",
            ""
        ]

        for med in medications_due:
            time_str = ""
            if 'next_dose_time' in med:
                time_obj = timezone.datetime.fromisoformat(med['next_dose_time'])
                time_str = f" ב-{time_obj.strftime('%H:%M')}"

            message_parts.append(f"• {med['name']} - {med['dosage']}{time_str}")

        message_text = "\n".join(message_parts)
    else:
        message_text = f"✅ כל התרופות ל-{child.first_name} ניתנו היום!"

    response_data = {
        'success': True,
        'timestamp': now.isoformat(),
        'child': {
            'name': child.name(),
            'slug': child.slug,
        },
        'medications_due_today': medications_due,
        'next_medication': next_medication,
        'total_active_medications': active_medications.count(),
        'message': message_text,
    }

    return Response(response_data)
