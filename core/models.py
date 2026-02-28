# -*- coding: utf-8 -*-
import datetime
import re

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.utils import OperationalError
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.text import format_lazy, slugify
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager as TaggitTaggableManager
from taggit.models import GenericTaggedItemBase, TagBase

from babybuddy.site_settings import NapSettings
from core.utils import random_color, timezone_aware_duration


def validate_date(date, field_name):
    """
    Confirm that a date is not in the future.
    :param date: a timezone aware date instance.
    :param field_name: the name of the field being checked.
    :return:
    """
    if date and date > timezone.localdate():
        raise ValidationError(
            {field_name: _("Date can not be in the future.")}, code="date_invalid"
        )


def validate_duration(model, max_duration=datetime.timedelta(hours=24)):
    """
    Basic sanity checks for models with a duration
    :param model: a model instance with 'start' and 'end' attributes
    :param max_duration: maximum allowed duration between start and end time
    :return:
    """
    if model.start and model.end:
        # Compare and calculate in UTC to account for DST changes between dates.
        start = model.start.astimezone(datetime.timezone.utc)
        end = model.end.astimezone(datetime.timezone.utc)
        if start > end:
            raise ValidationError(
                _("Start time must come before end time."), code="end_before_start"
            )
        if end - start > max_duration:
            raise ValidationError(_("Duration too long."), code="max_duration")


def validate_unique_period(queryset, model):
    """
    Confirm that model's start and end date do not intersect with other
    instances.
    :param queryset: a queryset of instances to check against.
    :param model: a model instance with 'start' and 'end' attributes
    :return:
    """
    if model.id:
        queryset = queryset.exclude(id=model.id)
    if model.start and model.end:
        if queryset.filter(start__lt=model.end, end__gt=model.start):
            raise ValidationError(
                _("Another entry intersects the specified time period."),
                code="period_intersection",
            )


def validate_time(time, field_name):
    """
    Confirm that a time is not in the future.
    :param time: a timezone aware datetime instance.
    :param field_name: the name of the field being checked.
    :return:
    """
    if time and time > timezone.localtime():
        raise ValidationError(
            {field_name: _("Date/time can not be in the future.")}, code="time_invalid"
        )


class Tag(TagBase):
    model_name = "tag"
    DARK_COLOR = "#101010"
    LIGHT_COLOR = "#EFEFEF"

    color = models.CharField(
        verbose_name=_("Color"),
        max_length=32,
        default=random_color,
        validators=[RegexValidator(r"^#[0-9a-fA-F]{6}$")],
    )
    last_used = models.DateTimeField(
        verbose_name=_("Last used"),
        default=timezone.now,
        blank=False,
    )

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = [Lower("name")]
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    @property
    def complementary_color(self):
        if not self.color:
            return self.DARK_COLOR

        r, g, b = [int(x, 16) for x in re.match("#(..)(..)(..)", self.color).groups()]
        yiq = ((r * 299) + (g * 587) + (b * 114)) // 1000
        if yiq >= 128:
            return self.DARK_COLOR
        else:
            return self.LIGHT_COLOR


class Tagged(GenericTaggedItemBase):
    tag = models.ForeignKey(
        Tag,
        verbose_name=_("Tag"),
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_items",
    )

    def save_base(self, *args, **kwargs):
        """
        Update last_used of the used tag, whenever it is used in a
        save-operation.
        """
        self.tag.last_used = timezone.now()
        self.tag.save()
        return super().save_base(*args, **kwargs)


class TaggableManager(TaggitTaggableManager):
    pass


class BMI(models.Model):
    model_name = "bmi"
    child = models.ForeignKey(
        "Child", on_delete=models.CASCADE, related_name="bmi", verbose_name=_("Child")
    )
    bmi = models.FloatField(blank=False, null=False, verbose_name=_("BMI"))
    date = models.DateField(
        blank=False, default=timezone.localdate, null=False, verbose_name=_("Date")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-date", "-id"]
        verbose_name = _("BMI")
        verbose_name_plural = _("BMI")

    def __str__(self):
        return str(_("BMI"))

    def clean(self):
        validate_date(self.date, "date")


class Child(models.Model):
    model_name = "child"
    first_name = models.CharField(max_length=255, verbose_name=_("First name"))
    last_name = models.CharField(
        blank=True, max_length=255, verbose_name=_("Last name")
    )
    birth_date = models.DateField(blank=False, null=False, verbose_name=_("Birth date"))
    birth_time = models.TimeField(blank=True, null=True, verbose_name=_("Birth time"))
    slug = models.SlugField(
        allow_unicode=True,
        blank=False,
        editable=False,
        max_length=100,
        unique=True,
        verbose_name=_("Slug"),
    )
    picture = models.ImageField(
        blank=True, null=True, upload_to="child/picture/", verbose_name=_("Picture")
    )
    feeding_mode = models.CharField(
        max_length=20,
        choices=[
            ('both', _('Breastfeeding & Bottle')),
            ('bottle_only', _('Bottle Only')),
            ('breast_only', _('Breastfeeding Only'))
        ],
        default='both',
        verbose_name=_('Feeding mode'),
        help_text=_('Select how this child is fed to customize the interface')
    )

    objects = models.Manager()

    cache_key_count = "core.child.count"

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["last_name", "first_name"]
        verbose_name = _("Child")
        verbose_name_plural = _("Children")

    def __str__(self):
        return self.name()

    def save(self, *args, **kwargs):
        self.slug = slugify(self, allow_unicode=True)
        super(Child, self).save(*args, **kwargs)
        cache.set(self.cache_key_count, Child.objects.count(), None)

    def delete(self, using=None, keep_parents=False):
        super(Child, self).delete(using, keep_parents)
        cache.set(self.cache_key_count, Child.objects.count(), None)

    def picture_file_exists(self):
        if not self.picture:
            return False

        name = getattr(self.picture, "name", None)
        if not name:
            return False

        try:
            return bool(self.picture.storage.exists(name))
        except (OSError, ValueError, TypeError, OperationalError):
            return False

    def name(self, reverse=False):
        if not self.last_name:
            return self.first_name
        if reverse:
            return "{}, {}".format(self.last_name, self.first_name)
        return "{} {}".format(self.first_name, self.last_name)

    def birth_datetime(self):
        if self.birth_time:
            return timezone.make_aware(
                datetime.datetime.combine(self.birth_date, self.birth_time)
            )
        return self.birth_date

    @classmethod
    def count(cls):
        """Get a (cached) count of total number of Child instances."""
        return cache.get_or_set(cls.cache_key_count, Child.objects.count, None)


class DiaperChange(models.Model):
    model_name = "diaperchange"
    child = models.ForeignKey(
        "Child",
        on_delete=models.CASCADE,
        related_name="diaper_change",
        verbose_name=_("Child"),
    )
    time = models.DateTimeField(
        blank=False, default=timezone.localtime, null=False, verbose_name=_("Time")
    )
    wet = models.BooleanField(verbose_name=_("Wet"))
    solid = models.BooleanField(verbose_name=_("Solid"))
    color = models.CharField(
        blank=True,
        choices=[
            ("black", _("Black")),
            ("brown", _("Brown")),
            ("green", _("Green")),
            ("yellow", _("Yellow")),
        ],
        max_length=255,
        verbose_name=_("Color"),
    )
    amount = models.FloatField(blank=True, null=True, verbose_name=_("Amount"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-time"]
        verbose_name = _("Diaper Change")
        verbose_name_plural = _("Diaper Changes")

    def __str__(self):
        return str(_("Diaper Change"))

    def attributes(self):
        attributes = []
        if self.wet:
            attributes.append(self._meta.get_field("wet").verbose_name)
        if self.solid:
            attributes.append(self._meta.get_field("solid").verbose_name)
        if self.color:
            attributes.append(self.get_color_display())
        return attributes

    def clean(self):
        validate_time(self.time, "time")


class Feeding(models.Model):
    model_name = "feeding"
    child = models.ForeignKey(
        "Child",
        on_delete=models.CASCADE,
        related_name="feeding",
        verbose_name=_("Child"),
    )
    start = models.DateTimeField(
        blank=False,
        default=timezone.localtime,
        null=False,
        verbose_name=_("Start time"),
    )
    end = models.DateTimeField(
        blank=False, default=timezone.localtime, null=False, verbose_name=_("End time")
    )
    duration = models.DurationField(
        editable=False, null=True, verbose_name=_("Duration")
    )
    type = models.CharField(
        choices=[
            ("breast milk", _("Breast milk")),
            ("formula", _("Formula")),
            ("fortified breast milk", _("Fortified breast milk")),
            ("solid food", _("Solid food")),
        ],
        max_length=255,
        verbose_name=_("Type"),
    )
    method = models.CharField(
        choices=[
            ("bottle", _("Bottle")),
            ("left breast", _("Left breast")),
            ("right breast", _("Right breast")),
            ("both breasts", _("Both breasts")),
            ("parent fed", _("Parent fed")),
            ("self fed", _("Self fed")),
        ],
        max_length=255,
        verbose_name=_("Method"),
    )
    amount = models.FloatField(blank=True, null=True, verbose_name=_("Amount"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-start"]
        verbose_name = _("Feeding")
        verbose_name_plural = _("Feedings")

    def __str__(self):
        return str(_("Feeding"))

    def save(self, *args, **kwargs):
        if self.start and self.end:
            self.duration = timezone_aware_duration(self.start, self.end)
        super(Feeding, self).save(*args, **kwargs)

    def clean(self):
        validate_time(self.start, "start")
        validate_duration(self)
        validate_unique_period(Feeding.objects.filter(child=self.child), self)


class HeadCircumference(models.Model):
    model_name = "head_circumference"
    child = models.ForeignKey(
        "Child",
        on_delete=models.CASCADE,
        related_name="head_circumference",
        verbose_name=_("Child"),
    )
    head_circumference = models.FloatField(
        blank=False, null=False, verbose_name=_("Head Circumference")
    )
    date = models.DateField(
        blank=False, default=timezone.localdate, null=False, verbose_name=_("Date")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-date", "-id"]
        verbose_name = _("Head Circumference")
        verbose_name_plural = _("Head Circumference")

    def __str__(self):
        return str(_("Head Circumference"))

    def clean(self):
        validate_date(self.date, "date")


class Height(models.Model):
    model_name = "height"
    child = models.ForeignKey(
        "Child",
        on_delete=models.CASCADE,
        related_name="height",
        verbose_name=_("Child"),
    )
    height = models.FloatField(blank=False, null=False, verbose_name=_("Height"))
    date = models.DateField(
        blank=False, default=timezone.localdate, null=False, verbose_name=_("Date")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-date", "-id"]
        verbose_name = _("Height")
        verbose_name_plural = _("Height")

    def __str__(self):
        return str(_("Height"))

    def clean(self):
        validate_date(self.date, "date")


class HeightPercentile(models.Model):
    model_name = "height percentile"
    age_in_days = models.DurationField(null=False)
    p3_height = models.FloatField(null=False)
    p15_height = models.FloatField(null=False)
    p50_height = models.FloatField(null=False)
    p85_height = models.FloatField(null=False)
    p97_height = models.FloatField(null=False)
    sex = models.CharField(
        null=False,
        max_length=255,
        choices=[
            ("girl", _("Girl")),
            ("boy", _("Boy")),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["age_in_days", "sex"], name="unique_age_sex_height"
            )
        ]


class Note(models.Model):
    model_name = "note"
    child = models.ForeignKey(
        "Child", on_delete=models.CASCADE, related_name="note", verbose_name=_("Child")
    )
    note = models.TextField(verbose_name=_("Note"))
    time = models.DateTimeField(
        blank=False, default=timezone.localtime, verbose_name=_("Time")
    )
    image = models.ImageField(
        blank=True, null=True, upload_to="notes/images/", verbose_name=_("Image")
    )
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-time"]
        verbose_name = _("Note")
        verbose_name_plural = _("Notes")

    def __str__(self):
        return str(_("Note"))


class Pumping(models.Model):
    model_name = "pumping"
    child = models.ForeignKey(
        "Child",
        on_delete=models.CASCADE,
        related_name="pumping",
        verbose_name=_("Child"),
    )
    start = models.DateTimeField(
        blank=False,
        default=timezone.localtime,
        null=False,
        verbose_name=_("Start time"),
    )
    end = models.DateTimeField(
        blank=False,
        default=timezone.localtime,
        null=False,
        verbose_name=_("End time"),
    )
    duration = models.DurationField(
        editable=False,
        null=True,
        verbose_name=_("Duration"),
    )
    amount = models.FloatField(blank=False, null=False, verbose_name=_("Amount"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-start"]
        verbose_name = _("Pumping")
        verbose_name_plural = _("Pumping")

    def __str__(self):
        return str(_("Pumping"))

    def save(self, *args, **kwargs):
        if self.start and self.end:
            self.duration = timezone_aware_duration(self.start, self.end)
        super(Pumping, self).save(*args, **kwargs)

    def clean(self):
        validate_time(self.start, "start")
        validate_duration(self)
        validate_unique_period(Pumping.objects.filter(child=self.child), self)


class Sleep(models.Model):
    model_name = "sleep"
    child = models.ForeignKey(
        "Child", on_delete=models.CASCADE, related_name="sleep", verbose_name=_("Child")
    )
    start = models.DateTimeField(
        blank=False,
        default=timezone.localtime,
        null=False,
        verbose_name=_("Start time"),
    )
    end = models.DateTimeField(
        blank=False, default=timezone.localtime, null=False, verbose_name=_("End time")
    )
    nap = models.BooleanField(null=False, blank=True, verbose_name=_("Nap"))
    duration = models.DurationField(
        editable=False, null=True, verbose_name=_("Duration")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()
    settings = NapSettings(_("Nap settings"))

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-start"]
        verbose_name = _("Sleep")
        verbose_name_plural = _("Sleep")

    def __str__(self):
        return str(_("Sleep"))

    def save(self, *args, **kwargs):
        if self.nap is None:
            self.nap = (
                Sleep.settings.nap_start_min
                <= timezone.localtime(self.start).time()
                <= Sleep.settings.nap_start_max
            )
        if self.start and self.end:
            self.duration = timezone_aware_duration(self.start, self.end)
            # Stop any active sleep timers for this child, since we now have
            # a completed sleep record.  This prevents the dashboard from
            # continuing to show "sleeping" after a wake-up is recorded via
            # a form (rather than through the timer toggle).
            Timer.objects.filter(
                child=self.child,
                active=True,
                name__in=["Sleep", "שינה"],
            ).update(active=False)
        super(Sleep, self).save(*args, **kwargs)

    def clean(self):
        validate_time(self.start, "start")
        validate_time(self.end, "end")
        validate_duration(self)
        validate_unique_period(Sleep.objects.filter(child=self.child), self)


class Temperature(models.Model):
    model_name = "temperature"
    child = models.ForeignKey(
        "Child",
        on_delete=models.CASCADE,
        related_name="temperature",
        verbose_name=_("Child"),
    )
    temperature = models.FloatField(
        blank=False, null=False, verbose_name=_("Temperature")
    )
    time = models.DateTimeField(
        blank=False, default=timezone.localtime, null=False, verbose_name=_("Time")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-time"]
        verbose_name = _("Temperature")
        verbose_name_plural = _("Temperature")

    def __str__(self):
        return str(_("Temperature"))

    def clean(self):
        validate_time(self.time, "time")


class Timer(models.Model):
    model_name = "timer"
    child = models.ForeignKey(
        "Child",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="timers",
        verbose_name=_("Child"),
    )
    name = models.CharField(
        blank=True, max_length=255, null=True, verbose_name=_("Name")
    )
    start = models.DateTimeField(
        default=timezone.now, blank=False, verbose_name=_("Start time")
    )
    active = models.BooleanField(default=True, editable=False, verbose_name=_("Active"))
    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="timers",
        verbose_name=_("User"),
    )

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-start"]
        verbose_name = _("Timer")
        verbose_name_plural = _("Timers")

    def __str__(self):
        return self.name or str(format_lazy(_("Timer #{id}"), id=self.id))

    @property
    def title_with_child(self):
        """Get Timer title with child name in parenthesis."""
        title = str(self)
        # Only actually add the name if there is more than one Child instance.
        if title and self.child and Child.count() > 1:
            title = format_lazy("{title} ({child})", title=title, child=self.child)
        return title

    @property
    def user_username(self):
        """Get Timer user's name with a preference for the full name."""
        if self.user.get_full_name():
            return self.user.get_full_name()
        return self.user.get_username()

    def duration(self):
        return timezone.now() - self.start

    def restart(self):
        """Restart the timer."""
        self.start = timezone.now()
        self.save()

    def stop(self):
        """Stop (delete) the timer."""
        self.delete()

    def save(self, *args, **kwargs):
        self.name = self.name or None
        super(Timer, self).save(*args, **kwargs)

    def clean(self):
        validate_time(self.start, "start")


class TummyTime(models.Model):
    model_name = "tummytime"
    child = models.ForeignKey(
        "Child",
        on_delete=models.CASCADE,
        related_name="tummy_time",
        verbose_name=_("Child"),
    )
    start = models.DateTimeField(
        blank=False,
        default=timezone.localtime,
        null=False,
        verbose_name=_("Start time"),
    )
    end = models.DateTimeField(
        blank=False, default=timezone.localtime, null=False, verbose_name=_("End time")
    )
    duration = models.DurationField(
        editable=False, null=True, verbose_name=_("Duration")
    )
    milestone = models.CharField(
        blank=True, max_length=255, verbose_name=_("Milestone")
    )
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-start"]
        verbose_name = _("Tummy Time")
        verbose_name_plural = _("Tummy Time")

    def __str__(self):
        return str(_("Tummy Time"))

    def save(self, *args, **kwargs):
        if self.start and self.end:
            self.duration = timezone_aware_duration(self.start, self.end)
        super(TummyTime, self).save(*args, **kwargs)

    def clean(self):
        validate_time(self.start, "start")
        validate_time(self.end, "end")
        validate_duration(self)
        validate_unique_period(TummyTime.objects.filter(child=self.child), self)


class Weight(models.Model):
    model_name = "weight"
    child = models.ForeignKey(
        "Child",
        on_delete=models.CASCADE,
        related_name="weight",
        verbose_name=_("Child"),
    )
    weight = models.FloatField(blank=False, null=False, verbose_name=_("Weight"))
    date = models.DateField(
        blank=False, default=timezone.localdate, null=False, verbose_name=_("Date")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes"))
    tags = TaggableManager(blank=True, through=Tagged)

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-date", "-id"]
        verbose_name = _("Weight")
        verbose_name_plural = _("Weight")

    def __str__(self):
        return str(_("Weight"))

    def clean(self):
        validate_date(self.date, "date")


class WeightPercentile(models.Model):
    model_name = "weight percentile"
    age_in_days = models.DurationField(null=False)
    p3_weight = models.FloatField(null=False)
    p15_weight = models.FloatField(null=False)
    p50_weight = models.FloatField(null=False)
    p85_weight = models.FloatField(null=False)
    p97_weight = models.FloatField(null=False)
    sex = models.CharField(
        null=False,
        max_length=255,
        choices=[
            ("girl", _("Girl")),
            ("boy", _("Boy")),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["age_in_days", "sex"], name="unique_age_sex"
            )
        ]

    def __str__(self):
        return f"Sex: {self.sex}, Age: {self.age_in_days} days, p3: {self.p3_weight} kg, p15: {self.p15_weight} kg, p50: {self.p50_weight} kg, p85: {self.p85_weight} kg, p97: {self.p97_weight} kg"


class Medication(models.Model):
    """
    Medication tracking - for vitamins, drops, medicines, etc.
    """
    model_name = "medication"

    child = models.ForeignKey(
        "Child",
        related_name="medications",
        on_delete=models.CASCADE,
        verbose_name=_("Child"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("Medication name (e.g., Vitamin D, Iron drops)"),
    )
    medication_type = models.CharField(
        max_length=50,
        choices=[
            ("vitamin", _("Vitamin")),
            ("drops", _("Drops")),
            ("medicine", _("Medicine")),
            ("supplement", _("Supplement")),
            ("other", _("Other")),
        ],
        default="vitamin",
        verbose_name=_("Type"),
    )
    dosage = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Dosage"),
        help_text=_("e.g., 5 drops, 1ml, 400 IU"),
    )
    frequency = models.CharField(
        max_length=50,
        choices=[
            ("once_daily", _("Once Daily")),
            ("twice_daily", _("Twice Daily")),
            ("three_times_daily", _("Three Times Daily")),
            ("every_other_day", _("Every Other Day")),
            ("weekly", _("Weekly")),
            ("as_needed", _("As Needed")),
            ("custom", _("Custom")),
        ],
        default="once_daily",
        verbose_name=_("Frequency"),
    )
    schedule_times = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Schedule times"),
        help_text=_("Comma-separated times (e.g., 09:00, 21:00)"),
    )
    start_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Start date"),
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("End date"),
        help_text=_("Leave blank for ongoing medication"),
    )
    active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
    )
    tags = TaggableManager(
        blank=True,
        through="core.Tagged",
        verbose_name=_("Tags"),
    )

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-active", "name"]
        verbose_name = _("Medication")
        verbose_name_plural = _("Medications")

    def __str__(self):
        return f"{self.name} - {self.child.name()}"

    def is_due_today(self):
        """Check if medication is due today based on frequency"""
        today = timezone.localdate()

        if not self.active:
            return False

        if self.end_date and today > self.end_date:
            return False

        if today < self.start_date:
            return False

        if self.frequency == "as_needed":
            return False

        if self.frequency == "weekly":
            # Check if it's been 7 days since last dose
            last_dose = self.doses.filter(given=True).order_by("-time").first()
            if last_dose:
                days_since = (today - last_dose.time.date()).days
                return days_since >= 7
            return True

        if self.frequency == "every_other_day":
            last_dose = self.doses.filter(given=True).order_by("-time").first()
            if last_dose:
                days_since = (today - last_dose.time.date()).days
                return days_since >= 2
            return True

        # For daily frequencies, check if already given or skipped today
        doses_today = self.doses.filter(
            time__date=today,
        ).count()

        frequency_map = {
            "once_daily": 1,
            "twice_daily": 2,
            "three_times_daily": 3,
        }

        required_doses = frequency_map.get(self.frequency, 1)
        return doses_today < required_doses

    def next_dose_time(self):
        """Get the next scheduled dose time"""
        if not self.schedule_times:
            return None

        now = timezone.now()
        today = timezone.localdate()
        times = [t.strip() for t in self.schedule_times.split(",")]

        for time_str in times:
            try:
                hour, minute = map(int, time_str.split(":"))
                scheduled_time = timezone.make_aware(
                    datetime.datetime.combine(today, datetime.time(hour, minute))
                )

                # Check if this dose was already given or skipped
                dose_given = self.doses.filter(
                    time__date=today,
                    time__hour=hour,
                ).exists()

                if not dose_given and scheduled_time > now:
                    return scheduled_time
            except (ValueError, IndexError):
                continue

        return None


class MedicationDose(models.Model):
    """
    Record of giving a medication dose
    """
    model_name = "medication dose"

    medication = models.ForeignKey(
        "Medication",
        related_name="doses",
        on_delete=models.CASCADE,
        verbose_name=_("Medication"),
    )
    child = models.ForeignKey(
        "Child",
        related_name="medication_doses",
        on_delete=models.CASCADE,
        verbose_name=_("Child"),
    )
    time = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Time"),
    )
    given = models.BooleanField(
        default=True,
        verbose_name=_("Given"),
        help_text=_("Was the medication actually given?"),
    )
    skipped_reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Skipped Reason"),
        help_text=_("Why was this dose skipped?"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
    )
    tags = TaggableManager(
        blank=True,
        through="core.Tagged",
        verbose_name=_("Tags"),
    )

    objects = models.Manager()

    class Meta:
        default_permissions = ("view", "add", "change", "delete")
        ordering = ["-time"]
        verbose_name = _("Medication dose")
        verbose_name_plural = _("Medication doses")

    def __str__(self):
        return f"{self.medication.name} - {self.time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        validate_date(self.time.date(), "time")
