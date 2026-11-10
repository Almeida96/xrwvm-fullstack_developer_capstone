"""Account and dealership endpoints for the local app and optional course services."""
import json
from datetime import date
from urllib.parse import quote

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST
from requests.exceptions import HTTPError, RequestException

from .local_store import dealer_rows, reviews_for
from .models import CarMake, CarModel, Dealership, DealerReview
from .restapis import get_request, post_review


def json_object(request):
    try:
        data = json.loads(request.body)
        if isinstance(data, dict):
            return data
    except (ValueError, UnicodeDecodeError):
        pass
    return None


@require_POST
@csrf_protect
def login_user(request):
    data = json_object(request)
    if data is None or any(not isinstance(data.get(key), str) or not 1 <= len(data[key]) <= 150
                           for key in ("userName", "password")):
        return JsonResponse({"error": "Username and password are required"}, status=400)
    user = authenticate(request, username=data["userName"], password=data["password"])
    if user is None:
        return JsonResponse({"error": "Invalid username or password"}, status=401)
    login(request, user)
    return JsonResponse({"userName": user.username, "status": "Authenticated"})


class RegistrationForm(forms.Form):
    userName = forms.RegexField(r"^[A-Za-z0-9_]{3,64}$", max_length=64)
    firstName = forms.CharField(max_length=150)
    lastName = forms.CharField(max_length=150)
    email = forms.EmailField(max_length=254)
    password = forms.CharField(min_length=8, max_length=128, strip=False)


@require_POST
@csrf_protect
def registration(request):
    data = json_object(request)
    if data is None or any(not isinstance(value, str) for value in data.values()):
        return JsonResponse({"error": "Invalid registration input"}, status=400)
    form = RegistrationForm(data)
    if not form.is_valid():
        return JsonResponse({"error": "Check the registration fields", "fields": form.errors}, status=400)
    values = form.cleaned_data
    user = get_user_model()(username=values["userName"], first_name=values["firstName"],
                            last_name=values["lastName"], email=values["email"])
    try:
        validate_password(values["password"], user)
    except ValidationError as error:
        return JsonResponse({"error": " ".join(error.messages)}, status=400)
    user.set_password(values["password"])
    try:
        with transaction.atomic():
            user.save()
    except IntegrityError:
        return JsonResponse({"error": "Username already exists"}, status=409)
    return JsonResponse({"userName": user.username, "status": "Registered"}, status=201)


@require_POST
@csrf_protect
def logout_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Not authenticated"}, status=401)
    logout(request)
    return JsonResponse({"status": "Logged out"})


def remote_result(endpoint):
    try:
        return get_request(endpoint), None
    except HTTPError as error:
        status = 404 if error.response is not None and error.response.status_code == 404 else 502
        return None, JsonResponse({"error": "Not found" if status == 404 else "Dealership service unavailable"}, status=status)
    except (RequestException, ValueError):
        return None, JsonResponse({"error": "Dealership service unavailable"}, status=502)


@require_GET
def get_dealerships(request):
    return get_dealers_by_state(request, "All")


@require_GET
def get_dealers_by_state(request, state):
    if settings.DEALERSHIP_STORAGE == "local":
        query = Dealership.objects.all()
        if state.lower() != "all":
            query = query.filter(state__iexact=state)
        dealers = dealer_rows(query[:1000])
    else:
        dealers, error = remote_result("fetchDealers/" + quote(state, safe=""))
        if error is not None:
            return error
    return JsonResponse({"status": 200, "dealers": dealers})


@require_GET
def get_dealer_details(request, dealer_id):
    if settings.DEALERSHIP_STORAGE == "local":
        dealers = dealer_rows(Dealership.objects.filter(pk=dealer_id))
        if not dealers:
            return JsonResponse({"error": "Dealership not found"}, status=404)
    else:
        dealers, error = remote_result(f"fetchDealer/{dealer_id}")
        if error is not None:
            return error
    return JsonResponse({"status": 200, "dealer": dealers})


@require_GET
def get_dealer_reviews(request, dealer_id):
    if settings.DEALERSHIP_STORAGE == "local":
        if not Dealership.objects.filter(pk=dealer_id).exists():
            return JsonResponse({"error": "Dealership not found"}, status=404)
        reviews = reviews_for(dealer_id)
    else:
        reviews, error = remote_result(f"fetchReviews/dealer/{dealer_id}")
        if error is not None:
            return error
    return JsonResponse(reviews, safe=False)


@require_POST
@csrf_protect
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Sign in before posting a review"}, status=401)
    data = json_object(request)
    if data is None or type(data.get("dealership")) is not int or type(data.get("car_year")) is not int:
        return JsonResponse({"error": "Invalid review input"}, status=400)
    strings = ("review", "car_make", "car_model", "purchase_date")
    if any(not isinstance(data.get(key), str) for key in strings) or type(data.get("purchase")) is not bool:
        return JsonResponse({"error": "Invalid review input"}, status=400)
    try:
        purchase_date = date.fromisoformat(data["purchase_date"])
    except ValueError:
        return JsonResponse({"error": "Invalid purchase date"}, status=400)
    text = data["review"].strip()
    car = CarModel.objects.filter(car_make__name=data["car_make"], name=data["car_model"], year=data["car_year"]).first()
    if not 1 <= len(text) <= 5000 or data["dealership"] < 1 or car is None or purchase_date > date.today():
        return JsonResponse({"error": "Missing or invalid review details"}, status=400)
    if settings.DEALERSHIP_STORAGE == "local":
        dealer = Dealership.objects.filter(pk=data["dealership"]).first()
        if dealer is None:
            return JsonResponse({"error": "Dealership not found"}, status=404)
        review = DealerReview.objects.create(dealership=dealer, author=request.user, car_model=car,
                                             text=text, purchase=data["purchase"], purchase_date=purchase_date)
        saved = {"id": review.pk}
    else:
        payload = {key: data[key] for key in (*strings, "dealership", "car_year", "purchase")}
        payload.update(name=request.user.get_full_name() or request.user.username, review=text)
        try:
            saved = post_review(payload)
        except (RequestException, ValueError):
            return JsonResponse({"error": "Review service unavailable"}, status=502)
    return JsonResponse({"status": 200, "review": saved}, status=201)


@require_GET
def get_cars(request):
    return JsonResponse({"status": 200,
        "CarMakes": list(CarMake.objects.values("id", "name", "description")),
        "CarModels": [{"id": model.pk, "CarMake": model.car_make.name, "CarModel": model.name,
                       "CarType": model.type, "CarYear": model.year}
                      for model in CarModel.objects.select_related("car_make").all()]})


@require_GET
def csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})


@require_GET
def session_status(request):
    return JsonResponse({"authenticated": request.user.is_authenticated, "username": request.user.get_username() if request.user.is_authenticated else None})
