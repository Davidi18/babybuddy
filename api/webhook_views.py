# -*- coding: utf-8 -*-
"""
Webhook Views לשילוב עם אוטומציות חיצוניות (n8n, Zapier, Make, וכו')
Webhook views for external automation integration
"""
import json
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.models import Child
from core.analytics import BabyAnalytics
from .llm_messages import get_message_generator


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def daily_summary_webhook(request):
    """
    Webhook לסיכום יומי - מציג נתונים של אתמול בברירת מחדל
    Daily summary webhook - shows yesterday's data by default (for morning reports)

    Query Parameters:
    - child: Child slug (default: first child)
    - date: Date for summary in YYYY-MM-DD format (default: yesterday)
    - use_llm: Whether to use LLM for cute messages (default: true)

    Examples:
    - GET /api/webhooks/daily-summary/  (yesterday's data)
    - GET /api/webhooks/daily-summary/?date=2025-01-15
    - GET /api/webhooks/daily-summary/?child=נעמי-מאייר&use_llm=true
    """
    import datetime

    child_slug = request.GET.get('child') or request.POST.get('child')
    date_param = request.GET.get('date') or request.POST.get('date')
    use_llm = request.GET.get('use_llm', 'true').lower() != 'false'

    # Get child
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

    # Get date - default to yesterday
    if date_param:
        try:
            summary_date = datetime.datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=400
            )
    else:
        # Default to yesterday
        summary_date = timezone.localdate() - datetime.timedelta(days=1)

    analytics = BabyAnalytics(child)

    # Get summary for the specified date
    yesterday_summary = analytics.get_daily_summary(date=summary_date)

    # Format date nicely
    date_str = summary_date.strftime('%d/%m/%Y')

    # Generate cute message with LLM
    msg_gen = get_message_generator()
    message_text = msg_gen.generate_daily_summary(
        child_name=child.first_name,
        summary_data=yesterday_summary,
        date_str=date_str,
        use_llm=use_llm
    )

    # Response data
    response_data = {
        'success': True,
        'timestamp': timezone.now().isoformat(),
        'summary_date': summary_date.isoformat(),
        'child': {
            'name': child.name(),
            'slug': child.slug,
        },
        'message': message_text,
        'data': yesterday_summary,
        'llm_enabled': msg_gen.is_available() and use_llm,
    }

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
    sleep_display = status.get('sleep_display_status')

    # טקסט סטטוס קצר
    status_parts = [f"👶 {child.name()}"]

    if last_feeding:
        status_parts.append(
            f"🍼 האכלה: לפני {last_feeding['time_since_formatted']}"
        )

    if sleep_display:
        status_parts.append(f"💤 {sleep_display['display_text']}")
    elif last_sleep:
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
        'sleep_display': sleep_display,
        'alerts': [],
    }

    # התראות
    feeding_display = status.get('feeding_display_status')
    is_feeding = feeding_display and feeding_display.get('mode') == 'feeding'
    if next_feeding and next_feeding['status'] == 'overdue' and not is_feeding:
        response_data['alerts'].append({
            'type': 'feeding_overdue',
            'message': next_feeding['message'],
        })

    is_sleeping = sleep_display and sleep_display.get('mode') == 'sleeping'
    if next_sleep and next_sleep['status'] in ('overtired', 'getting_tired') and not is_sleeping:
        response_data['alerts'].append({
            'type': next_sleep['status'],
            'message': next_sleep['message'],
            'icon': '😴' if next_sleep['status'] == 'getting_tired' else '😫',
        })

    return Response(response_data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def alerts_webhook(request):
    """
    Unified Smart Alerts Webhook with LLM-generated cute messages

    Supports customizable thresholds, quiet hours, snooze, and medication alerts.
    Uses Claude AI to generate varied, cute messages (optional).

    Query Parameters:
    - child: Child slug (default: first child)
    - feeding_threshold: Minutes overdue to trigger feeding alert (default: 15)
    - sleep_threshold: Minutes awake to trigger overtired alert (default: 90)
    - diaper_threshold: Minutes since last diaper to alert (default: 180)
    - medication_threshold: Minutes before/after dose to alert (default: 0)
    - snooze_minutes: Minutes to wait before re-alerting (default: 30)
    - quiet_hours_start: Hour to start quiet period (default: 22)
    - quiet_hours_end: Hour to end quiet period (default: 7)
    - respect_quiet_hours: Whether to respect quiet hours (default: true)
    - use_llm: Whether to use LLM for messages (default: true)

    Examples:
    - GET /api/webhooks/alerts/
    - GET /api/webhooks/alerts/?child=emma
    - GET /api/webhooks/alerts/?feeding_threshold=20&use_llm=true
    """
    child_slug = request.GET.get('child') or request.POST.get('child')

    # Thresholds (in minutes)
    feeding_threshold = int(request.GET.get('feeding_threshold', 15))
    sleep_threshold = int(request.GET.get('sleep_threshold', 90))
    diaper_threshold = int(request.GET.get('diaper_threshold', 180))
    medication_threshold = int(request.GET.get('medication_threshold', 0))

    # Quiet hours configuration
    quiet_hours_start = int(request.GET.get('quiet_hours_start', 22))
    quiet_hours_end = int(request.GET.get('quiet_hours_end', 7))
    respect_quiet_hours = request.GET.get('respect_quiet_hours', 'true').lower() != 'false'

    # Snooze configuration
    snooze_minutes = int(request.GET.get('snooze_minutes', 30))

    # LLM configuration
    use_llm = request.GET.get('use_llm', 'true').lower() != 'false'

    # Get child
    if child_slug:
        try:
            child = Child.objects.get(slug=child_slug)
        except Child.DoesNotExist:
            return Response({'error': f'Child not found: {child_slug}'}, status=404)
    else:
        child = Child.objects.first()
        if not child:
            return Response({'error': 'No children in the system'}, status=404)

    # Check quiet hours
    current_hour = timezone.localtime().hour
    is_quiet_hours = False

    if respect_quiet_hours:
        if quiet_hours_start > quiet_hours_end:
            is_quiet_hours = current_hour >= quiet_hours_start or current_hour < quiet_hours_end
        else:
            is_quiet_hours = quiet_hours_start <= current_hour < quiet_hours_end

    if is_quiet_hours:
        return Response({
            'success': True,
            'has_alerts': False,
            'message': f'שעות שקטות ({quiet_hours_start}:00-{quiet_hours_end}:00) - לא שולחים התראות',
            'quiet_hours': True,
            'current_hour': current_hour,
            'child': {
                'name': child.name(),
                'slug': child.slug,
            },
        })

    # Get analytics
    analytics = BabyAnalytics(child)
    status = analytics.get_current_status()

    # Initialize LLM message generator
    msg_gen = get_message_generator()

    alerts = []

    # Check feeding (skip if baby is currently being fed)
    feeding_display = status.get('feeding_display_status')
    is_currently_feeding = feeding_display and feeding_display.get('mode') == 'feeding'
    next_feeding = status.get('next_feeding_prediction')
    if next_feeding and not is_currently_feeding:
        minutes_until = next_feeding.get('minutes_until_next', 0)
        if minutes_until < -feeding_threshold:
            alert_key = f'alert_feeding_{child.id}'

            if cache.add(alert_key, True, timeout=snooze_minutes * 60):
                alert_details = {
                    'minutes_overdue': abs(minutes_until),
                    'threshold_used': feeding_threshold,
                }

                cute_message = msg_gen.generate_alert_message(
                    child_name=child.first_name,
                    alert_type='feeding_overdue',
                    details=alert_details,
                    use_llm=use_llm
                )

                alerts.append({
                    'type': 'feeding_overdue',
                    'severity': 'high',
                    'title': f'{child.first_name} רעבה!',
                    'message': cute_message,
                    'minutes_overdue': abs(minutes_until),
                    'threshold_used': feeding_threshold,
                })

    # Check sleep (skip if baby is currently sleeping)
    sleep_display = status.get('sleep_display_status')
    is_currently_sleeping = sleep_display and sleep_display.get('mode') == 'sleeping'
    next_sleep = status.get('next_sleep_prediction')
    if next_sleep and not is_currently_sleeping:
        minutes_awake = next_sleep.get('minutes_awake', 0)
        if minutes_awake > sleep_threshold:
            alert_key = f'alert_sleep_{child.id}'

            if cache.add(alert_key, True, timeout=snooze_minutes * 60):
                alert_details = {
                    'minutes_awake': minutes_awake,
                    'threshold_used': sleep_threshold,
                }

                cute_message = msg_gen.generate_alert_message(
                    child_name=child.first_name,
                    alert_type='overtired',
                    details=alert_details,
                    use_llm=use_llm
                )

                alerts.append({
                    'type': 'overtired',
                    'severity': 'high',
                    'title': f'{child.first_name} עייפה מאוד!',
                    'message': cute_message,
                    'minutes_awake': minutes_awake,
                    'threshold_used': sleep_threshold,
                })

    # Check diaper
    last_diaper = status.get('last_diaper')
    if last_diaper:
        minutes_since = last_diaper.get('time_since_minutes', 0)
        if minutes_since > diaper_threshold:
            alert_key = f'alert_diaper_{child.id}'

            if cache.add(alert_key, True, timeout=snooze_minutes * 60):
                alert_details = {
                    'hours_since': last_diaper['time_since_hours'],
                    'threshold_used': diaper_threshold,
                }

                cute_message = msg_gen.generate_alert_message(
                    child_name=child.first_name,
                    alert_type='diaper_overdue',
                    details=alert_details,
                    use_llm=use_llm
                )

                alerts.append({
                    'type': 'diaper_overdue',
                    'severity': 'medium',
                    'title': 'זמן לחיתול',
                    'message': cute_message,
                    'hours_since': last_diaper['time_since_hours'],
                    'threshold_used': diaper_threshold,
                })

    # Check medications
    try:
        from django.db.models import Q
        from core.models import Medication

        today = timezone.localdate()
        now = timezone.now()

        active_meds = Medication.objects.filter(
            child=child,
            active=True,
            start_date__lte=today,
        ).filter(Q(end_date__isnull=True) | Q(end_date__gte=today))

        next_med = None
        next_time = None

        for med in active_meds:
            if not med.is_due_today():
                continue
            med_time = med.next_dose_time()
            if not med_time:
                continue
            if next_time is None or med_time < next_time:
                next_time = med_time
                next_med = med

        if next_med and next_time:
            minutes_until = int((next_time - now).total_seconds() / 60)

            if minutes_until <= medication_threshold:
                alert_key = f'alert_medication_{child.id}_{next_med.id}'

                if cache.add(alert_key, True, timeout=snooze_minutes * 60):
                    alert_details = {
                        'medication': {
                            'id': next_med.id,
                            'name': next_med.name,
                            'dosage': next_med.dosage,
                            'type': next_med.medication_type,
                        },
                        'next_dose_time': next_time.isoformat(),
                        'minutes_until': minutes_until,
                        'threshold_used': medication_threshold,
                    }

                    cute_message = msg_gen.generate_alert_message(
                        child_name=child.first_name,
                        alert_type='medication_due',
                        details=alert_details,
                        use_llm=use_llm
                    )

                    alerts.append({
                        'type': 'medication_due',
                        'severity': 'high' if minutes_until < 0 else 'medium',
                        'title': 'זמן לתרופה',
                        'message': cute_message,
                        'medication': {
                            'id': next_med.id,
                            'name': next_med.name,
                            'dosage': next_med.dosage,
                            'type': next_med.medication_type,
                        },
                        'next_dose_time': next_time.isoformat(),
                        'minutes_until': minutes_until,
                        'threshold_used': medication_threshold,
                    })
    except Exception:
        pass

    # No alerts
    if not alerts:
        return Response({
            'success': True,
            'has_alerts': False,
            'message': 'הכל בסדר! אין התראות',
            'quiet_hours': False,
            'thresholds': {
                'feeding': feeding_threshold,
                'sleep': sleep_threshold,
                'diaper': diaper_threshold,
                'medication': medication_threshold,
            },
            'child': {
                'name': child.name(),
                'slug': child.slug,
            },
        })

    # Has alerts
    return Response({
        'success': True,
        'has_alerts': True,
        'alert_count': len(alerts),
        'alerts': alerts,
        'quiet_hours': False,
        'thresholds': {
            'feeding': feeding_threshold,
            'sleep': sleep_threshold,
            'diaper': diaper_threshold,
            'medication': medication_threshold,
        },
        'snooze_minutes': snooze_minutes,
        'llm_enabled': msg_gen.is_available() and use_llm,
        'child': {
            'name': child.name(),
            'slug': child.slug,
        },
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
