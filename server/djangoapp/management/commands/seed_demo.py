"""Seed the course catalog without deleting existing dealers, users or reviews."""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from djangoapp.models import Dealership
from djangoapp.populate import initiate


class Command(BaseCommand):
    help = "Load the bundled example dealerships and cars; preserve existing records."

    @transaction.atomic
    def handle(self, *args, **options):
        path = Path(__file__).resolve().parents[3] / "database/data/dealerships.json"
        rows = json.loads(path.read_text(encoding="utf-8"))["dealerships"]
        added = 0
        for row in rows:
            _, created = Dealership.objects.get_or_create(
                pk=row["id"], defaults={key: str(row[key]) for key in
                ("full_name", "city", "state", "address", "zip")})
            added += created
        initiate()
        self.stdout.write(f"Dealership catalog ready: {Dealership.objects.count()} records ({added} new).")
