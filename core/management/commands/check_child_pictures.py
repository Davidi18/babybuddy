from django.core.management.base import BaseCommand

from core.models import Child


class Command(BaseCommand):
    help = "Check for Child.picture references where the underlying file is missing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="If set, clears Child.picture when the file is missing.",
        )

    def handle(self, *args, **options):
        fix = bool(options.get("fix"))

        qs = Child.objects.exclude(picture="").exclude(picture__isnull=True)
        total = qs.count()
        missing = []

        for child in qs.iterator():
            if not child.picture_file_exists():
                missing.append(child)

        if not missing:
            self.stdout.write(self.style.SUCCESS(f"✅ OK: {total} children with pictures, none missing"))
            return

        self.stdout.write(
            self.style.WARNING(
                f"⚠️ Found {len(missing)} children with picture set but file missing (out of {total} with pictures)"
            )
        )

        for child in missing:
            name = child.name()
            path = getattr(child.picture, "name", "")
            self.stdout.write(f"- {child.pk} {name}: {path}")

        if not fix:
            self.stdout.write("\nRun again with --fix to clear these broken picture references.")
            return

        for child in missing:
            child.picture = None
            child.save(update_fields=["picture"])

        self.stdout.write(self.style.SUCCESS(f"✅ Cleared picture field for {len(missing)} children"))
