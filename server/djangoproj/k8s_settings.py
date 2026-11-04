"""Settings applied only when the Django container runs in the lab Kubernetes cluster.

Lab-friendly defaults below are intentionally not suitable for public production use.
For a real production deployment set DJANGO_ALLOWED_HOSTS and
DJANGO_CSRF_TRUSTED_ORIGINS to exact domains and supply DJANGO_SECRET_KEY.
"""
import os

from .settings import *  # noqa: F403,F401


DEBUG = False

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", SECRET_KEY)

ALLOWED_HOSTS = [
    item.strip()
    for item in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if item.strip()
]

CSRF_TRUSTED_ORIGINS = [
    item.strip()
    for item in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "https://*.proxy.cognitiveclass.ai",
    ).split(",")
    if item.strip()
]

# The proxy may terminate TLS before forwarding traffic to Kubernetes.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if "django.middleware.csrf.CsrfViewMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(
        MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware"),
        "django.middleware.csrf.CsrfViewMiddleware",
    )
