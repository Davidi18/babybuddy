# -*- coding: utf-8 -*-
import json
import logging

from django.conf import settings

from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)


def send_push_notification(user, title, body, url="/", tag="babybuddy-notification"):
    """
    Send a push notification to all subscribed devices for a user.
    """
    from babybuddy.models import PushSubscription

    subscriptions = PushSubscription.objects.filter(user=user)
    if not subscriptions.exists():
        logger.debug("No push subscriptions for user %s", user.username)
        return 0

    if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
        logger.warning("VAPID keys not configured, cannot send push notifications")
        return 0

    payload = json.dumps(
        {
            "title": title,
            "body": body,
            "url": url,
            "tag": tag,
        }
    )

    vapid_claims = {
        "sub": "mailto:{}".format(settings.VAPID_ADMIN_EMAIL),
    }

    sent = 0
    for sub in subscriptions:
        try:
            webpush(
                subscription_info=sub.to_subscription_info(),
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims=vapid_claims,
            )
            sent += 1
        except WebPushException as e:
            if e.response and e.response.status_code in (404, 410):
                logger.info(
                    "Removing expired subscription %s for user %s",
                    sub.endpoint[:50],
                    user.username,
                )
                sub.delete()
            else:
                logger.error(
                    "Failed to send push to %s: %s",
                    sub.endpoint[:50],
                    str(e),
                )
        except Exception as e:
            logger.error("Unexpected error sending push: %s", str(e))

    return sent


def send_push_to_all_users(title, body, url="/", tag="babybuddy-notification"):
    """
    Send a push notification to all users who have subscriptions.
    """
    from django.contrib.auth import get_user_model
    from babybuddy.models import PushSubscription

    User = get_user_model()
    user_ids = (
        PushSubscription.objects.values_list("user_id", flat=True).distinct()
    )
    total = 0
    for user in User.objects.filter(id__in=user_ids):
        total += send_push_notification(user, title, body, url, tag)
    return total
