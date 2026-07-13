import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from store.models import Product


class Command(BaseCommand):
    help = "Upload all local product images to Cloudinary"

    def handle(self, *args, **kwargs):
        migrated = 0

        for product in Product.objects.all():
            if not product.image:
                continue

            local_path = os.path.join(settings.MEDIA_ROOT, product.image.name)

            if not os.path.exists(local_path):
                self.stdout.write(
                    self.style.WARNING(
                        f"Image not found: {local_path}"
                    )
                )
                continue

            with open(local_path, "rb") as f:
                filename = os.path.basename(local_path)

                # Save image again using Cloudinary storage
                product.image.save(filename, File(f), save=True)

            migrated += 1
            self.stdout.write(
                self.style.SUCCESS(f"Uploaded: {product.name}")
            )

        self.stdout.write(
            self.style.SUCCESS(f"\nDone! {migrated} images uploaded.")
        )