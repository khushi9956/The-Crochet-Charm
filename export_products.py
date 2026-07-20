import os
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "the_crochet_charm.settings")

import django
django.setup()

from store.models import Product

data = []

for p in Product.objects.all():
    data.append({
        "model": "store.product",
        "pk": p.pk,
        "fields": {
            "name": p.name,
            "price": str(p.price),
            "image": p.image.name if p.image else "",
            "description": p.description,
        }
    })

with open("products.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"✅ Exported {len(data)} products successfully!")