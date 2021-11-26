from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe


@require_POST
@csrf_exempt
def webhook(request):
    """Listen for webhooks from Stripe"""
    # SETUP
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # GET THE WEBHOOK DATA AND VERIFY ITS SIGNATURE
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
    except ValueError as e:
        # INVALID PAYLOAD
        return HttpResponse(content=e, status=400)
    except stripe.error.SignatureVerificationError as e:
        # INVALID SIGNATURE
        return HttpResponse(content=e, status=400)
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # SET UP A WEBHOOK HANDLER
    handler = StripeWH_Handler(request)

    # MAP WEBHOOK EVENTS TO RELEVANT HANDLER FUNCTIONS
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # GET THE WEBHOOK TYPE FROM STRIPE
    event_type = event['type']

    # IF THERE'S A HANDLER FOR IT, GET IT FROM THE EVENT MAP
    # USE THE GENERIC ONE BY DEFAULT
    event_handler = event_map.get(event_type, handler.handle_event)

    # CALL THE EVENT HANDLER WITH THE EVENT
    response = event_handler(event)
    return response