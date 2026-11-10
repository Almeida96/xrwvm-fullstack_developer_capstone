"""Persistent local dealership data, using the same response shapes as the course API."""

from .models import DealerReview


def dealer_rows(query):
    return list(query.values("id", "full_name", "city", "state", "address", "zip"))


def reviews_for(dealer_id):
    return [
        {"id": review.pk, "name": review.author.get_full_name() or review.author.username,
         "dealership": review.dealership_id, "review": review.text,
         "purchase": review.purchase, "purchase_date": review.purchase_date.isoformat(),
         "car_make": review.car_model.car_make.name, "car_model": review.car_model.name,
         "car_year": review.car_model.year}
        for review in DealerReview.objects.filter(dealership_id=dealer_id)
        .select_related("author", "car_model__car_make").order_by("-created_at", "-id")[:200]
    ]
