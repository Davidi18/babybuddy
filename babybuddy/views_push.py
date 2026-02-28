# -*- coding: utf-8 -*-
import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from babybuddy.models import PushSubscription
from babybuddy.push import send_push_notification


@require_GET
def vapid_public_key(request):
    """Return the VAPID public key for client-side push subscription."""
    return JsonResponse({"vapid_public_key": settings.VAPID_PUBLIC_KEY})


@require_POST
def push_subscribe(request):
    """Subscribe to push notifications."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    endpoint = data.get("endpoint")
    keys = data.get("keys", {})
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")

    if not all([endpoint, p256dh, auth]):
        return JsonResponse({"error": "Missing subscription data"}, status=400)

    sub, created = PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            "user": request.user,
            "p256dh": p256dh,
            "auth": auth,
        },
    )

    return JsonResponse(
        {
            "status": "subscribed" if created else "updated",
            "id": sub.id,
        }
    )


@require_POST
def push_unsubscribe(request):
    """Unsubscribe from push notifications."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    endpoint = data.get("endpoint")
    if not endpoint:
        return JsonResponse({"error": "Missing endpoint"}, status=400)

    deleted, _ = PushSubscription.objects.filter(
        user=request.user, endpoint=endpoint
    ).delete()

    return JsonResponse({"status": "unsubscribed", "deleted": deleted})


@require_POST
def push_test(request):
    """Send a test push notification to the current user."""
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=401)

    sent = send_push_notification(
        user=request.user,
        title="Baby Buddy",
        body="Push notifications are working!",
        url="/",
        tag="test-notification",
    )

    return JsonResponse({"status": "sent", "devices": sent})
