# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from babybuddy.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.models import Child
from core.analytics import BabyAnalytics


class Dashboard(LoginRequiredMixin, TemplateView):
    # TODO: Use .card-deck in this template once BS4 is finalized.
    template_name = "dashboard/dashboard.html"

    # Show the overall dashboard or a child dashboard if one Child instance.
    def get(self, request, *args, **kwargs):
        children = Child.objects.count()
        if children == 0:
            return HttpResponseRedirect(reverse("babybuddy:welcome"))
        elif children == 1:
            return HttpResponseRedirect(
                reverse("dashboard:dashboard-child", args={Child.objects.first().slug})
            )
        return super(Dashboard, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Dashboard, self).get_context_data(**kwargs)
        context["objects"] = Child.objects.all().order_by(
            "last_name", "first_name", "id"
        )
        return context


class ChildDashboard(PermissionRequiredMixin, DetailView):
    model = Child
    permission_required = ("core.view_child",)
    template_name = "dashboard/child.html"


class ChildAnalyticsDashboard(PermissionRequiredMixin, DetailView):
    """
    דף אנליטיקה מלא עם גרפים וסטטיסטיקות
    Full analytics dashboard with charts and statistics
    """

    model = Child
    permission_required = ("core.view_child",)
    template_name = "dashboard/analytics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        child = self.object
        analytics = BabyAnalytics(child)

        # Get analytics data
        context["analytics"] = analytics
        context["current_status"] = analytics.get_current_status()
        context["daily_summary"] = analytics.get_daily_summary()
        context["feeding_stats"] = analytics.get_feeding_stats(days=7)
        context["sleep_stats"] = analytics.get_sleep_stats(days=7)
        context["diaper_stats"] = analytics.get_diaper_stats(days=7)

        return context
