from django.db import models
from django.conf import settings
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
        validators=[MinValueValidator(1900), MaxValueValidator(2100)]
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


class Dealership(models.Model):
    full_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, db_index=True)
    address = models.CharField(max_length=250)
    zip = models.CharField(max_length=20)

    class Meta:
        ordering = ["id"]


class DealerReview(models.Model):
    dealership = models.ForeignKey(Dealership, on_delete=models.PROTECT, related_name="reviews")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    car_model = models.ForeignKey(CarModel, on_delete=models.PROTECT)
    text = models.TextField(max_length=5000)
    purchase = models.BooleanField()
    purchase_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
