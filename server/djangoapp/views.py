# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
import logging
import json
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from datetime import date
from requests.exceptions import RequestException, HTTPError
from .restapis import get_request, post_review
from .models import CarMake, CarModel
# from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
@require_POST
def login_user(request):
    """Authenticate a JSON credential object without treating invalid input as a server error."""
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid login input"}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"error": "Invalid login input"}, status=400)
    username = data.get('userName')
    password = data.get('password')
    if not isinstance(username, str) or not username or not isinstance(password, str) or not password:
        return JsonResponse({"error": "Username and password are required"}, status=400)
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"error": "Invalid username or password"}, status=401)
    login(request, user)
    return JsonResponse({"userName": user.get_username(), "status": "Authenticated"})

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Only a signed-in session can be logged out.
    if not request.user.is_authenticated:
        return JsonResponse({"status": "Not authenticated"}, status=401)

    username = request.user.get_username()
    logout(request)
    return JsonResponse({"userName": username, "status": "Logged out"})

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

# Return dealership data to the React frontend through the Node.js backend.
def get_dealerships(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        dealers = get_request("fetchDealers")
    except (RequestException, ValueError) as error:
        logger.warning("Unable to fetch dealerships: %s", error)
        return JsonResponse({"error": "Dealership service unavailable"}, status=502)

    return JsonResponse({"status": 200, "dealers": dealers})

def get_dealers_by_state(request, state):
    """Return dealerships filtered by state, or all dealerships for 'All'."""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        dealers = get_request(f"fetchDealers/{state}")
    except (RequestException, ValueError) as error:
        logger.warning("Unable to fetch dealerships in state %s: %s", state, error)
        return JsonResponse({"error": "Dealership service unavailable"}, status=502)

    return JsonResponse({"status": 200, "dealers": dealers})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    """Return reviews for a dealership through the Node.js/MongoDB service."""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        reviews = get_request(f"fetchReviews/dealer/{dealer_id}")
    except (RequestException, ValueError) as error:
        logger.warning("Unable to fetch dealership reviews: %s", error)
        return JsonResponse({"error": "Dealership reviews service unavailable"}, status=502)

    return JsonResponse(reviews, safe=False)

# Get a dealership by numeric ID (proxy to Node.js/MongoDB).
def get_dealer_details(request, dealer_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        dealer_list = get_request(f"fetchDealer/{dealer_id}")
    except HTTPError as error:
        if error.response is not None and error.response.status_code == 404:
            return JsonResponse({"error": "Dealership not found"}, status=404)
        logger.warning("Backend error fetching dealership %s: %s", dealer_id, error)
        return JsonResponse({"error": "Dealership service unavailable"}, status=502)
    except (RequestException, ValueError) as error:
        logger.warning("Unable to fetch dealership %s: %s", dealer_id, error)
        return JsonResponse({"error": "Dealership service unavailable"}, status=502)

    return JsonResponse({"status": 200, "dealer": dealer_list})

# Persist a signed-in user's dealership review in the Node.js/MongoDB service.
@login_required(login_url="/login/")
@require_POST
@csrf_protect
def add_review(request):
    try:
        body = json.loads(request.body)
        dealer_id = int(body.get("dealership"))
        year = int(body.get("car_year"))
        review_text = str(body.get("review", "")).strip()
        car_make = str(body.get("car_make", "")).strip()
        car_model = str(body.get("car_model", "")).strip()
        purchase_date = str(body.get("purchase_date", "")).strip()
        purchased = body.get("purchase")
        date.fromisoformat(purchase_date)
    except (TypeError, ValueError, AttributeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid review input"}, status=400)

    if (
        dealer_id < 1
        or not review_text
        or year < 2015
        or year > 2023
        or type(purchased) is not bool
        or not CarModel.objects.filter(
            car_make__name=car_make, name=car_model, year=year
        ).exists()
    ):
        return JsonResponse({"error": "Missing or invalid review details"}, status=400)

    data = {
        "name": request.user.get_full_name().strip() or request.user.get_username(),
        "dealership": dealer_id,
        "review": review_text,
        "purchase": purchased,
        "purchase_date": purchase_date,
        "car_make": car_make,
        "car_model": car_model,
        "car_year": year,
    }
    try:
        saved = post_review(data)
    except (RequestException, ValueError) as error:
        logger.warning("Unable to save dealership review: %s", error)
        return JsonResponse({"error": "Review service unavailable"}, status=502)
    return JsonResponse({"status": 200, "review": saved})

# List the car makes and models used by the React post-review form.
def get_cars(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    car_makes = list(CarMake.objects.values("id", "name", "description"))
    car_models = [
        {
            "id": model.id,
            "CarMake": model.car_make.name,
            "CarModel": model.name,
            "CarType": model.type,
            "CarYear": model.year,
        }
        for model in CarModel.objects.select_related("car_make").all()
    ]
    return JsonResponse({
        "status": 200,
        "CarMakes": car_makes,
        "CarModels": car_models,
    })
