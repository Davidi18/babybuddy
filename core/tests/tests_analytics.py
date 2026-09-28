# -*- coding: utf-8 -*-
import datetime
from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core import models
from core.analytics import BabyAnalytics


class TwoNapWakeWindowTestCase(TestCase):
    """9-12 months: 2 naps, wake windows 2.5-3 / 3-3.5 / 3.5-4 hours."""

    def setUp(self):
        call_command("migrate", verbosity=0)
        self.day = timezone.localdate() - datetime.timedelta(days=1)
        self.child = models.Child.objects.create(
            first_name="Naomi",
            last_name="Test",
            birth_date=self.day - datetime.timedelta(days=int(9.5 * 30.44)),
        )
        # Night sleep ending 06:30
        self._sleep(-1, 19, 0, 0, 6, 30, nap=False)

    def _at(self, hour, minute, day_offset=0):
        return timezone.make_aware(
            datetime.datetime.combine(
                self.day + datetime.timedelta(days=day_offset),
                datetime.time(hour, minute),
            )
        )

    def _sleep(self, start_offset, sh, sm, end_offset, eh, em, nap):
        models.Sleep.objects.create(
            child=self.child,
            start=self._at(sh, sm, start_offset),
            end=self._at(eh, em, end_offset),
            nap=nap,
        )

    def _prediction(self, hour, minute):
        with mock.patch(
            "django.utils.timezone.now", return_value=self._at(hour, minute)
        ):
            return BabyAnalytics(self.child).predict_next_sleep()

    def _predict(self, hour, minute):
        return self._prediction(hour, minute)["wake_window"]

    def assertWindow(self, window, period, min_minutes, max_minutes):
        self.assertEqual(window["period"], period)
        self.assertEqual(window["min_minutes"], min_minutes)
        self.assertEqual(window["max_minutes"], max_minutes)

    def test_morning_window_after_night_sleep(self):
        self.assertWindow(self._predict(8, 0), "morning", 150.0, 180.0)

    def test_between_naps_window_after_first_nap(self):
        # First nap ends at 10:30 - still before 11:00 on the clock, but this
        # is the window between naps, not the morning window.
        self._sleep(0, 9, 15, 0, 10, 30, nap=True)
        self.assertWindow(self._predict(10, 45), "midday", 180.0, 210.0)

    def test_before_bedtime_window_after_second_nap(self):
        # Second nap ends at 14:45 - before 15:00 on the clock.
        self._sleep(0, 9, 15, 0, 10, 30, nap=True)
        self._sleep(0, 13, 30, 0, 14, 45, nap=True)
        self.assertWindow(self._predict(14, 50), "before_bedtime", 210.0, 240.0)

    def test_bedtime_window_is_predicted_in_the_evening(self):
        # Second nap ends at 15:00, so the bedtime window is 18:30-19:00.
        self._sleep(0, 9, 15, 0, 10, 30, nap=True)
        self._sleep(0, 13, 45, 0, 15, 0, nap=True)
        prediction = self._prediction(18, 45)
        self.assertWindow(prediction["wake_window"], "before_bedtime", 210.0, 240.0)
        self.assertEqual(prediction["status"], "getting_tired")

    def test_no_prediction_at_night(self):
        self._sleep(0, 9, 15, 0, 10, 30, nap=True)
        self._sleep(0, 13, 45, 0, 15, 0, nap=True)
        self.assertIsNone(self._prediction(20, 0))
        self.assertIsNone(self._prediction(5, 30))

    def test_age_recommended_range(self):
        with mock.patch("django.utils.timezone.now", return_value=self._at(8, 0)):
            self.assertEqual(
                BabyAnalytics(self.child)._get_age_based_wake_window(),
                (150.0, 240.0),
            )
