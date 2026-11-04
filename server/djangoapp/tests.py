from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import CarMake, CarModel


class DealershipAppTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(
            username="ci-test-user",
            password="StrongCIExample123!",
        )
        cls.make = CarMake.objects.create(name="Toyota", description="Toyota vehicles")
        cls.model = CarModel.objects.create(
            car_make=cls.make,
            name="Camry",
            type="SEDAN",
            year=2023,
        )

    def test_home_page_is_available_without_login(self):
        response = self.client.get("/dealers/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Available dealerships")

    def test_car_catalog_api_returns_make_and_model(self):
        response = self.client.get("/djangoapp/get_cars")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["CarMakes"][0]["name"], "Toyota")
        self.assertEqual(data["CarModels"][0]["CarModel"], "Camry")

    def test_post_review_page_requires_login(self):
        response = self.client.get("/postreview/15/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_authenticated_post_review_page_shows_form(self):
        self.client.force_login(self.user)
        response = self.client.get("/postreview/15/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="review-form"')
        self.assertContains(response, "Signed in as: ci-test-user")
