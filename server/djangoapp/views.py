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
from django.views.decorators.csrf import csrf_exempt
from requests.exceptions import RequestException
from .restapis import get_request
# from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

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

# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
# ...
