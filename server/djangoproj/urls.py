"""djangoproj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', TemplateView.as_view(template_name="Login.html"), name='login_page'),
    path('dealers/', TemplateView.as_view(template_name="Home.html"), name='dealers_page'),
    path('dealers/<str:state>/', TemplateView.as_view(template_name="Home.html"), name='dealers_filtered_page'),
    path('dealer/<int:dealer_id>/', TemplateView.as_view(template_name="DealerDetails.html"), name='dealer_details_page'),
    path('postreview/<int:dealer_id>/', ensure_csrf_cookie(login_required(TemplateView.as_view(template_name="PostReview.html"), login_url='/login/')), name='post_review_page'),
    path('djangoapp/', include('djangoapp.urls')),
    path('', TemplateView.as_view(template_name="Home.html")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
