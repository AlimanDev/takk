from apps.payment.stripe_webhook import stripe_webhook
from django.urls import path

from django.views.generic import TemplateView


urlpatterns = [
    path('save-card/', TemplateView.as_view(template_name="base.html")),
    path('payment/', TemplateView.as_view(template_name="payment.html")),
    path('webhook/', stripe_webhook),
]


