# -*- coding: utf-8 -*-
import base64

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from django.core.management.base import BaseCommand

from py_vapid import Vapid


class Command(BaseCommand):
    help = "Generate VAPID key pair for Web Push notifications"

    def handle(self, *args, **options):
        v = Vapid()
        v.generate_keys()

        pub_raw = v.public_key.public_bytes(
            Encoding.X962, PublicFormat.UncompressedPoint
        )
        pub_b64 = base64.urlsafe_b64encode(pub_raw).rstrip(b"=").decode()

        priv_numbers = v.private_key.private_numbers()
        priv_raw = priv_numbers.private_value.to_bytes(32, "big")
        priv_b64 = base64.urlsafe_b64encode(priv_raw).rstrip(b"=").decode()

        self.stdout.write("\nVAPID Keys Generated Successfully!\n")
        self.stdout.write("=" * 50)
        self.stdout.write(
            "\nAdd these to your .env file or environment variables:\n"
        )
        self.stdout.write("\nVAPID_PUBLIC_KEY={}".format(pub_b64))
        self.stdout.write("VAPID_PRIVATE_KEY={}".format(priv_b64))
        self.stdout.write("VAPID_ADMIN_EMAIL=your-email@example.com\n")
        self.stdout.write("=" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                "\nDon't forget to restart the server after adding the keys!"
            )
        )
