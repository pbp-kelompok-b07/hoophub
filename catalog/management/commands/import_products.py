import csv
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from catalog.models import Product
from django.db import transaction

# Helper to parse date; adjust the formats to match your CSV
def parse_date(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unknown date format: {s!r}")

class Command(BaseCommand):
    help = "Import products from a CSV file into the Product model"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            type=str,
            help="Path to CSV file (e.g. datasets/product_dataset.csv)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing rows (matched by name + brand) instead of skipping",
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        csv_path = opts["csv_path"]
        do_update = opts["update"]

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames:
                    raise CommandError("CSV has no header row.")
                required = {"name", "brand"}
                missing = required - set(h.strip() for h in reader.fieldnames)
                if missing:
                    raise CommandError(f"CSV missing required headers: {missing}")

                created, updated, skipped = 0, 0, 0

                for row in reader:
                    # Normalize/clean inputs from CSV
                    name = (row.get("name") or "").strip()
                    brand = (row.get("brand") or "").strip()
                    category = (row.get("category") or "").strip() or None
                    description = (row.get("description") or "").strip() or ""
                    image = (row.get("image") or "").strip() or None
                    link = (row.get("link") or "").strip() or None  # optional
                    release_date = None
                    if row.get("release_date"):
                        release_date = parse_date(row["release_date"])

                    # Price & stock with safety
                    def to_int(val, default=0):
                        try:
                            return int(str(val).replace(".", "").replace(",", "").strip())
                        except Exception:
                            return default

                    price = to_int(row.get("price"), 0)
                    stock = to_int(row.get("stock"), 0)

                    # Decide availability: if stock provided use it; else fall back to >0 price etc.
                    is_available = stock > 0 if row.get("stock") is not None else True

                    # Upsert by (name, brand)
                    if do_update:
                        obj, was_created = Product.objects.update_or_create(
                            name=name,
                            brand=brand,
                            defaults={
                                "category": category,
                                "description": description,
                                "price": price,
                                "stock": stock,
                                "image": image,
                                "release_date": release_date,
                                "is_available": is_available,
                            },
                        )
                        if was_created:
                            created += 1
                        else:
                            updated += 1
                    else:
                        obj, was_created = Product.objects.get_or_create(
                            name=name,
                            brand=brand,
                            defaults={
                                "category": category,
                                "description": description,
                                "price": price,
                                "stock": stock,
                                "image": image,
                                "release_date": release_date,
                                "is_available": is_available,
                            },
                        )
                        if was_created:
                            created += 1
                        else:
                            skipped += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Done. created={created}, updated={updated}, skipped={skipped}"
                    )
                )

        except FileNotFoundError:
            raise CommandError(f"CSV not found: {csv_path}")
        except Exception as e:
            raise CommandError(str(e))
