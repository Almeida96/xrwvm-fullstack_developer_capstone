# Uncomment the imports before you add the code
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'
urlpatterns = [
    # # path for registration

    # path for login
    path(route='login', view=views.login_user, name='login'),
    path(route='logout', view=views.logout_request, name='logout'),

    # List dealerships for the React frontend
    path(route='get_dealers', view=views.get_dealerships, name='get_dealerships'),
    path(route='get_dealers/<str:state>', view=views.get_dealers_by_state, name='get_dealers_by_state'),
    path(route='dealer/<int:dealer_id>', view=views.get_dealer_details, name='dealer_details'),

    # Dealer reviews API (Django proxy to the Node.js service)
    path(route='get_dealer_reviews/<int:dealer_id>', view=views.get_dealer_reviews, name='get_dealer_reviews'),

    # Car make/model listings for the review form
    path(route='get_cars', view=views.get_cars, name='get_cars'),

    # Post a signed-in customer's dealership review
    path(route='add_review', view=views.add_review, name='add_review'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
