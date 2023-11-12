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
import stripe


class StripeWH_Handler:
    """
    Handle Stripe webhooks
    """

    def __init__(self, request):
        """
        Initialize the StripeWH_Handler with a request object
        """
        self.request = request

    def _send_confirmation_email(self, order):
        """
        Send a confirmation email to the customer
        """
        cust_email = order.email
        subject = render_to_string(
            'checkout/emails/confirmation-email-subject.txt',
            {'order': order})

        body = render_to_string(
            'checkout/emails/confirmation-email-body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        body_html = render_to_string(
            'checkout/emails/confirmation-email-body.html',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,  # This will be the plain-text version
            settings.DEFAULT_FROM_EMAIL,
            [cust_email],
            html_message=body_html  # This is the HTML version
        )

    def handle_event(self, event):
        """
        Handle unhandled or unknown events
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=HTTPStatus.OK)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle successful payment intents.
        """
        try:
            # Extract important info from event data
            intent = event.data.object
            pid = intent.id
            latest_charge = intent.latest_charge
            metadata = intent.metadata

            # Deserialize the cart data from metadata
            cart_str = metadata.get('cart', '[]')
            username = metadata.get('username', 'AnonymousUser')

            try:
                cart_data = json.loads(cart_str)
            except json.JSONDecodeError:
                content = (f'Webhook received: {event["type"]} | '
                           'ERROR: JSON decoding error')
                return HttpResponse(content=content,
                                    status=HTTPStatus.INTERNAL_SERVER_ERROR)

            cart_info = cart_data

            # Get the billing details from Stripe
            charge_obj = stripe.Charge.retrieve(latest_charge)
            billing_details = charge_obj.get('billing_details', {})

        except KeyError as e:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        # Update or fetch user profile based on username
        profile = None
        if username != 'AnonymousUser':
            profile = get_object_or_404(UserProfile, user__username=username)

            profile.save()

        # Check if the order already exists
        order_exists = False
        attempt = 1
        name_split = []
        if billing_details and 'name' in billing_details:
            name = billing_details.get('name', '')
            if name:
                name_split = name.split(' ')

        while attempt <= 5:
            try:
                first_name = name_split[0] if len(name_split) > 0 else ''
                last_name = name_split[1] if len(name_split) > 1 else ''
                email = (billing_details.get('email', '')
                         if billing_details else '')
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
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=HTTPStatus.INTERNAL_SERVER_ERROR)

        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | '
                    f'SUCCESS: Created order in webhook',
            status=HTTPStatus.OK)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle payment failures
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=HTTPStatus.OK)
