# -*- coding: utf-8 -*-
"""
🎯 Smart Webhook Views - גרסה משופרת
Webhook views עם thresholds מותאמים, שעות שקטות, ו-snooze

הוסף את זה לסוף הקובץ api/webhook_views.py הקיים
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.utils import timezone
from core.models import Child
from core.analytics import BabyAnalytics


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def smart_alerts_webhook(request):
    """
    🎯 Webhook התראות חכם - עם thresholds מותאמים, שעות שקטות, ו-snooze
    Smart alerts webhook with custom thresholds, quiet hours, and snooze
    
    Parameters:
        child: slug של הילד
        feeding_threshold: דקות איחור להאכלה (ברירת מחדל: 15)
        sleep_threshold: דקות ער מקסימום (ברירת מחדל: 90)
        diaper_threshold: דקות מחיתול אחרון (ברירת מחדל: 180)
        quiet_hours_start: שעה להתחלת שעות שקטות (ברירת מחדל: 22)
        quiet_hours_end: שעה לסיום שעות שקטות (ברירת מחדל: 7)
        snooze_minutes: דקות להמתנה בין התראות זהות (ברירת מחדל: 30)
        respect_quiet_hours: האם לכבד שעות שקטות (ברירת מחדל: true)
    
    Examples:
        GET /api/webhooks/smart-alerts/?child=emma
        GET /api/webhooks/smart-alerts/?feeding_threshold=20&sleep_threshold=100
        GET /api/webhooks/smart-alerts/?quiet_hours_start=23&quiet_hours_end=6
        GET /api/webhooks/smart-alerts/?respect_quiet_hours=false
    """
    # קבלת פרמטרים
    child_slug = request.GET.get('child') or request.POST.get('child')
    
    # Thresholds מותאמים
    feeding_threshold = int(request.GET.get('feeding_threshold', 15))
    sleep_threshold = int(request.GET.get('sleep_threshold', 90))
    diaper_threshold = int(request.GET.get('diaper_threshold', 180))  # 3 שעות
    
    # שעות שקטות
    quiet_hours_start = int(request.GET.get('quiet_hours_start', 22))
    quiet_hours_end = int(request.GET.get('quiet_hours_end', 7))
    respect_quiet_hours = request.GET.get('respect_quiet_hours', 'true').lower() != 'false'
    
    # Snooze
    snooze_minutes = int(request.GET.get('snooze_minutes', 30))
    
    # בחירת ילד
    if child_slug:
        try:
            child = Child.objects.get(slug=child_slug)
        except Child.DoesNotExist:
            return Response({'error': f'Child not found: {child_slug}'}, status=404)
    else:
        child = Child.objects.first()
        if not child:
            return Response({'error': 'No children in the system'}, status=404)
    
    # 🌙 בדיקת שעות שקטות
    current_hour = timezone.localtime().hour
    is_quiet_hours = False
    
    if respect_quiet_hours:
        if quiet_hours_start > quiet_hours_end:
            # חוצה חצות (לדוגמה: 22:00-07:00)
            is_quiet_hours = current_hour >= quiet_hours_start or current_hour < quiet_hours_end
        else:
            # לא חוצה חצות (לדוגמה: 01:00-06:00)
            is_quiet_hours = quiet_hours_start <= current_hour < quiet_hours_end
    
    if is_quiet_hours:
        return Response({
            'success': True,
            'has_alerts': False,
            'message': f'🌙 שעות שקטות ({quiet_hours_start}:00-{quiet_hours_end}:00) - לא שולחים התראות',
            'quiet_hours': True,
            'current_hour': current_hour,
            'child': {
                'name': child.name(),
                'slug': child.slug,
            },
        })
    
    # קבלת נתונים
    analytics = BabyAnalytics(child)
    status = analytics.get_current_status()
    
    alerts = []
    
    # 🍼 בדיקת האכלה עם threshold מותאם
    next_feeding = status.get('next_feeding_prediction')
    if next_feeding:
        minutes_until = next_feeding.get('minutes_until_next', 0)
        if minutes_until < -feeding_threshold:  # עבר הזמן
            alert_key = f'alert_feeding_{child.id}'
            
            # בדיקת snooze
            if not cache.get(alert_key):
                alerts.append({
                    'type': 'feeding_overdue',
                    'severity': 'high',
                    'title': f'{child.first_name} רעבה!',
                    'message': f'עבר זמן האכלה! איחור של {abs(minutes_until)} דקות',
                    'minutes_overdue': abs(minutes_until),
                    'threshold_used': feeding_threshold,
                })
                
                # הגדרת snooze
                cache.set(alert_key, True, timeout=snooze_minutes * 60)
    
    # 😴 בדיקת שינה עם threshold מותאם
    next_sleep = status.get('next_sleep_prediction')
    if next_sleep:
        minutes_awake = next_sleep.get('minutes_awake', 0)
        if minutes_awake > sleep_threshold:
            alert_key = f'alert_sleep_{child.id}'
            
            if not cache.get(alert_key):
                alerts.append({
                    'type': 'overtired',
                    'severity': 'high',
                    'title': f'{child.first_name} עייפה מאוד!',
                    'message': f'ערה כבר {minutes_awake} דקות! זמן לישון',
                    'minutes_awake': minutes_awake,
                    'threshold_used': sleep_threshold,
                })
                
                cache.set(alert_key, True, timeout=snooze_minutes * 60)
    
    # 🧷 בדיקת חיתול עם threshold מותאם
    last_diaper = status.get('last_diaper')
    if last_diaper:
        minutes_since = last_diaper.get('time_since_minutes', 0)
        if minutes_since > diaper_threshold:
            alert_key = f'alert_diaper_{child.id}'
            
            if not cache.get(alert_key):
                from .llm_messages import format_time_since
                time_text = format_time_since(last_diaper['time_since_hours'])
                alerts.append({
                    'type': 'diaper_overdue',
                    'severity': 'medium',
                    'title': 'זמן לחיתול',
                    'message': f'עברו {time_text} מחיתול אחרון',
                    'hours_since': last_diaper['time_since_hours'],
                    'threshold_used': diaper_threshold,
                })
                
                cache.set(alert_key, True, timeout=snooze_minutes * 60)
    
    # אם אין התראות
    if not alerts:
        return Response({
            'success': True,
            'has_alerts': False,
            'message': 'הכל בסדר! אין התראות ✅',
            'quiet_hours': False,
            'thresholds': {
                'feeding': feeding_threshold,
                'sleep': sleep_threshold,
                'diaper': diaper_threshold,
            },
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
        'alerts': alerts,
        'quiet_hours': False,
        'thresholds': {
            'feeding': feeding_threshold,
            'sleep': sleep_threshold,
            'diaper': diaper_threshold,
        },
        'snooze_minutes': snooze_minutes,
        'child': {
            'name': child.name(),
            'slug': child.slug,
        },
        'timestamp': timezone.now().isoformat(),
    })
