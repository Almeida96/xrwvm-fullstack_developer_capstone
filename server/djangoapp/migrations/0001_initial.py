# Initial car catalog models for the IBM Full Stack Capstone.
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CarMake",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="CarModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("SUV", "SUV"),
                            ("SEDAN", "Sedan"),
                            ("HATCHBACK", "Hatchback"),
                            ("COUPE", "Coupe"),
                            ("CONVERTIBLE", "Convertible"),
                            ("MINIVAN", "Minivan"),
                            ("PICKUP", "Pickup"),
                            ("WAGON", "Wagon"),
                            ("OTHER", "Other"),
                        ],
                        default="OTHER",
                        max_length=20,
                    ),
                ),
                (
                    "year",
                    models.PositiveIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(2015),
                            django.core.validators.MaxValueValidator(2023),
                        ]
                    ),
                ),
                (
                    "car_make",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="models",
                        to="djangoapp.carmake",
                    ),
                ),
            ],
            options={"ordering": ["car_make__name", "name", "year"]},
        ),
        migrations.AddConstraint(
            model_name="carmodel",
            constraint=models.UniqueConstraint(
                fields=("car_make", "name", "year", "type"),
                name="unique_car_model_year_and_type",
            ),
        ),
    ]
