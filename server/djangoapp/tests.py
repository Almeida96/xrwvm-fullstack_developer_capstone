from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.core.management import call_command
from unittest.mock import patch

from .models import CarMake, CarModel, Dealership, DealerReview


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


class LocalWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        DealershipAppTests.setUpTestData.__func__(cls)

    def setUp(self):
        self.dealer = Dealership.objects.create(full_name="Example Cars", city="Example", state="Texas",
                                               address="1 Sample Road", zip="00000")
        self.payload = {"dealership": self.dealer.pk, "review": "Helpful service", "purchase": True,
                        "purchase_date": "2023-01-01", "car_make": "Toyota", "car_model": "Camry", "car_year": 2023}

    def test_seed_is_idempotent_and_does_not_remove_reviews(self):
        self.client.force_login(self.user)
        self.client.post('/djangoapp/add_review', self.payload, content_type='application/json')
        call_command('seed_demo', verbosity=0)
        counts = (Dealership.objects.count(), CarModel.objects.count())
        call_command('seed_demo', verbosity=0)
        self.assertEqual(counts, (Dealership.objects.count(), CarModel.objects.count()))
        self.assertEqual(DealerReview.objects.count(), 1)

    @patch('djangoapp.views.get_request', side_effect=AssertionError('No network in local mode'))
    def test_browse_filter_details_and_persist_review(self, remote):
        self.assertEqual(self.client.get('/djangoapp/get_dealers/texas').json()['dealers'][0]['full_name'], 'Example Cars')
        self.assertEqual(self.client.get('/djangoapp/get_dealers/Ohio').json()['dealers'], [])
        self.assertEqual(self.client.get('/djangoapp/dealer/9999').status_code, 404)
        self.assertEqual(self.client.post('/djangoapp/add_review', self.payload, content_type='application/json').status_code, 401)
        self.client.force_login(self.user)
        self.payload['name'] = 'Forged author'
        response = self.client.post('/djangoapp/add_review', self.payload, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        saved = DealerReview.objects.get()
        self.assertEqual(saved.author, self.user)
        other_client = Client()
        reviews = other_client.get(f'/djangoapp/get_dealer_reviews/{self.dealer.pk}').json()
        self.assertEqual(reviews[0]['review'], 'Helpful service')
        self.assertEqual(reviews[0]['name'], self.user.username)

    def test_review_validation_rejects_coercion_oversized_text_and_future_dates(self):
        self.client.force_login(self.user)
        for key, value in [('dealership', True), ('car_year', 2023.5), ('review', ['x']),
                           ('review', 'x' * 5001), ('purchase', 'true'), ('purchase_date', '2999-01-01')]:
            with self.subTest(key=key, value=str(value)[:30]):
                response = self.client.post('/djangoapp/add_review', {**self.payload, key: value}, content_type='application/json')
                self.assertEqual(response.status_code, 400)
        self.assertEqual(DealerReview.objects.count(), 0)

    def test_registration_login_and_logout_enforce_csrf(self):
        browser = Client(enforce_csrf_checks=True)
        browser.get('/register/')
        payload = dict(userName='new_reader', firstName='Example', lastName='Reader',
                       email='reader@example.invalid', password='A-long-unusual-phrase-749!')
        self.assertEqual(browser.post('/djangoapp/register', payload, content_type='application/json').status_code, 403)
        headers = {'HTTP_X_CSRFTOKEN': browser.cookies['csrftoken'].value}
        self.assertEqual(browser.post('/djangoapp/register', payload, content_type='application/json', **headers).status_code, 201)
        self.assertEqual(browser.post('/djangoapp/register', payload, content_type='application/json', **headers).status_code, 409)
        account = get_user_model().objects.get(username='new_reader')
        self.assertNotEqual(account.password, payload['password'])
        self.assertEqual(browser.post('/djangoapp/login', payload, content_type='application/json', **headers).status_code, 200)
        self.assertEqual(browser.get('/djangoapp/logout').status_code, 405)
        self.assertEqual(browser.post('/djangoapp/logout').status_code, 403)
        self.assertEqual(browser.post('/djangoapp/logout', HTTP_X_CSRFTOKEN=browser.cookies['csrftoken'].value).status_code, 200)

    def test_weak_password_and_invalid_registration_do_not_create_users(self):
        payload = dict(userName='new_reader', firstName='A', lastName='B', email='a@example.invalid', password='password')
        self.assertEqual(self.client.post('/djangoapp/register', payload, content_type='application/json').status_code, 400)
        self.assertFalse(get_user_model().objects.filter(username='new_reader').exists())

    @override_settings(DEALERSHIP_STORAGE='remote')
    @patch('djangoapp.views.get_request')
    def test_remote_adapter_remains_explicit(self, remote):
        remote.return_value = [{'id': 77, 'full_name': 'Remote demo'}]
        self.assertEqual(self.client.get('/djangoapp/get_dealers').json()['dealers'][0]['id'], 77)
        remote.assert_called_once_with('fetchDealers/All')
