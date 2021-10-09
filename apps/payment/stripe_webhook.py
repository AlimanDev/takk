from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import json

from apps.payment import models as payment_models
from apps.payment.logic import logics as payment_logics
from apps.orders import models as order_models
from apps.companies import models as company_models
from apps.users import models as user_models
from django.conf import settings

# FIXME:   https://stripe.com/docs/webhooks/signatures сделать так в продакшене

@require_POST
@csrf_exempt
def stripe_webhook(request):
    # Webhook stripe
    payload = request.body
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        event = stripe.Event.construct_from(
          json.loads(payload), stripe.api_key)
        payment_logics.processing_event(event)  # TODO: нужно перенести в celery task
    except ValueError as e:
        print(str(e))
        return HttpResponse(status=400)

    return HttpResponse(status=200)
