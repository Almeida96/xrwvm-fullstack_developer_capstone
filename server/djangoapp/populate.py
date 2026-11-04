"""Load sample car makes and models from the capstone's vehicle data.

Run after migrations:
    python3 manage.py shell -c "from djangoapp.populate import initiate; initiate()"
"""
import json
from pathlib import Path

from django.db import transaction

from .models import CarMake, CarModel


def initiate():
    data_path = (
        Path(__file__).resolve().parent.parent
        / "database"
        / "data"
        / "car_records.json"
    )

    with data_path.open(encoding="utf-8") as input_file:
        records = json.load(input_file)["cars"]

    make_count = 0
    model_count = 0

    with transaction.atomic():
        for vehicle in records:
            brand_name = vehicle["make"].strip()
            make, added_make = CarMake.objects.get_or_create(
                name=brand_name,
                defaults={"description": f"{brand_name} vehicles"},
            )
            make_count += int(added_make)

            _, added_model = CarModel.objects.get_or_create(
                car_make=make,
                name=vehicle["model"].strip(),
                year=int(vehicle["year"]),
                type=vehicle["bodyType"].strip().upper(),
            )
            model_count += int(added_model)

    print(
        f"Car data ready: {CarMake.objects.count()} makes and "
        f"{CarModel.objects.count()} models "
        f"({make_count} new makes, {model_count} new models)."
    )
