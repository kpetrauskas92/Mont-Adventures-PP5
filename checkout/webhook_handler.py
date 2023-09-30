from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from http import HTTPStatus
from .models import Order, OrderLineItem
from trip_packages.models import Trips, AvailableDate
from profiles.models import UserProfile
import json
import time
import logging

# Configure logging
logger = logging.getLogger(__name__)


class StripeWH_Handler:
    """Handle Stripe webhooks."""

    def __init__(self, request):
        """Initialize the StripeWH_Handler with a request object."""
        self.request = request

    def _send_confirmation_email(self, order):
        """Send a confirmation email to the customer."""
        cust_email = order.email
        subject = render_to_string(
            'checkout/emails/confirmation-email-subject.txt', {'order': order})
        body = render_to_string(
            'checkout/emails/confirmation-email-body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [cust_email])

    def handle_event(self, event):
        """Handle unhandled or unknown events."""
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=HTTPStatus.OK)

    def handle_payment_intent_succeeded(self, event):
        """Handle payment_intent.succeeded events."""
        try:
            # Extract important info from event data
            intent = event.data.object
            pid = intent.id
            metadata = intent.metadata
            cart_info = json.loads(metadata.get('cart', '{}'))
            username = metadata.get('username', None)
            charges_data = intent.get('charges', {}).get('data', [])

            # Check if charges are available
            if not charges_data:
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | '
                            f'ERROR: No charges found',
                    status=HTTPStatus.BAD_REQUEST)

            billing_details = charges_data[0].get('billing_details', None)

        except KeyError as e:
            logger.error(f"KeyError: {e}")
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=HTTPStatus.INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=HTTPStatus.INTERNAL_SERVER_ERROR)

        # Handle user profile and billing details
        profile = None
        if username != 'AnonymousUser':
            profile = get_object_or_404(UserProfile, user__username=username)
            if billing_details:
                profile.default_country = billing_details.get(
                    'address', {}).get('country', None)
                profile.save()

        # Check for existing order
        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                name_split = billing_details.get('name', '').split(' ')
                first_name = name_split[0] if len(name_split) > 0 else ''
                last_name = name_split[1] if len(name_split) > 1 else ''
                email = billing_details.get('email', '')
                order = Order.objects.get(
                    first_name__iexact=first_name,
                    last_name__iexact=last_name,
                    email__iexact=email,
                    stripe_pid=pid)
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | '
                        f'SUCCESS: Verified order already in database',
                status=HTTPStatus.OK)

        try:
            with transaction.atomic():
                # Create order and line items
                order = Order.objects.create(
                    user_profile=profile,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    stripe_pid=pid)

                for item in cart_info:
                    trip = Trips.objects.get(id=item['trip_id'])
                    available_date = AvailableDate.objects.get(
                        id=item['available_date_id'])
                    if available_date.remaining_slots() >= item['guests']:
                        available_date.booked_slots += item['guests']
                        available_date.save()
                        OrderLineItem.objects.create(
                            order=order,
                            trip=trip,
                            available_date=available_date,
                            guests=item['guests'])
                    else:
                        raise Exception(
                            f'Not enough slots available for {trip.name} on '
                            f'{available_date.start_date}')

        except Exception as e:
            if order:
                order.delete()
            logger.error(f"An error occurred while creating order: {e}")
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=HTTPStatus.INTERNAL_SERVER_ERROR)

        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | '
                    f'SUCCESS: Created order in webhook',
            status=HTTPStatus.OK)

    def handle_payment_intent_payment_failed(self, event):
        """Handle payment failures."""
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=HTTPStatus.OK)
