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

    def test_login_rejects_malformed_json_and_credentials(self):
        for payload in ('{', '[]', 'null', '{}', '{"userName": null, "password": "x"}',
                        '{"userName": "ci-test-user", "password": {}}'):
            with self.subTest(payload=payload):
                response = self.client.post('/djangoapp/login', payload, content_type='application/json')
                self.assertEqual(response.status_code, 400)
                self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_only_accepts_post(self):
        self.assertEqual(self.client.get('/djangoapp/login').status_code, 405)

    def test_login_rejects_wrong_password_and_authenticates_valid_user(self):
        response = self.client.post('/djangoapp/login', {
            'userName': self.user.username, 'password': 'wrong-password',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        response = self.client.post('/djangoapp/login', {
            'userName': self.user.username, 'password': 'StrongCIExample123!',
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'Authenticated')
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.pk))
