from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class CarMake(models.Model):
    """Automotive brand, such as Toyota or Nissan."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CarModel(models.Model):
    """Car model and model year belonging to a brand."""

    TYPE_CHOICES = [
        ("SUV", "SUV"),
        ("SEDAN", "Sedan"),
        ("HATCHBACK", "Hatchback"),
        ("COUPE", "Coupe"),
        ("CONVERTIBLE", "Convertible"),
        ("MINIVAN", "Minivan"),
        ("PICKUP", "Pickup"),
        ("WAGON", "Wagon"),
        ("OTHER", "Other"),
    ]

    car_make = models.ForeignKey(
        CarMake, on_delete=models.CASCADE, related_name="models"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="OTHER")
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(2015), MaxValueValidator(2023)]
    )

    class Meta:
        ordering = ["car_make__name", "name", "year"]
        constraints = [
            models.UniqueConstraint(
                fields=["car_make", "name", "year", "type"],
                name="unique_car_model_year_and_type",
            )
        ]

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"
