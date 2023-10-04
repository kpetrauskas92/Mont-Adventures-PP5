from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import UserProfile
from checkout.models import Order


class OrderAdminInline(admin.TabularInline):
    """
    Inline admin class to display orders related to a user profile
    in the Django admin interface.
    """
    model = Order
    fields = ('order_number', 'trip_name', 'start_date', 'end_date',
              'order_total', 'grand_total')
    readonly_fields = ('order_number', 'trip_name', 'start_date',
                       'end_date', 'order_total', 'grand_total')
    extra = 0
    show_change_link = True

    def trip_name(self, obj):
        """
        Return the name of the trip for the given order.
        """
        line_item = obj.lineitems.first()
        return line_item.trip.name if line_item else '-'

    def start_date(self, obj):
        """
        Return the start date of the trip for the given order.
        """
        line_item = obj.lineitems.first()
        return line_item.available_date.start_date if line_item else '-'

    def end_date(self, obj):
        """
        Return the end date of the trip for the given order.
        """
        line_item = obj.lineitems.first()
        return line_item.available_date.end_date if line_item else '-'

    trip_name.short_description = 'Trip Name'
    start_date.short_description = 'Start Date'
    end_date.short_description = 'End Date'


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    """
    Admin class for UserProfile model. This class defines how the UserProfile
    model should be displayed and managed in the Django admin interface.
    """
    inlines = [OrderAdminInline]
    list_display = ('get_first_name', 'get_last_name',
                    'get_email', 'customer_id', 'is_verified')
    search_fields = ('user__username', 'customer_id', 'user__is_active')

    def get_queryset(self, request):
        """
        Customize the queryset to exclude superusers and staff users.
        """
        qs = super().get_queryset(request)
        return qs.exclude(user__is_superuser=True, user__is_staff=True)

    def get_first_name(self, obj):
        """
        Return the first name of the user associated with the UserProfile.
        """
        return obj.user.first_name
    get_first_name.admin_order_field = 'user__first_name'
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        """
        Return the last name of the user associated with the UserProfile.
        """
        return obj.user.last_name
    get_last_name.admin_order_field = 'user__last_name'
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        """
        Return the email of the user associated with the UserProfile.
        """
        return obj.user.email
    get_email.admin_order_field = 'user__email'
    get_email.short_description = 'Email'

    def is_verified(self, obj):
        """
        Check if the user associated with the UserProfile is active.
        """
        return obj.user.is_active
    is_verified.admin_order_field = 'user__is_active'
    is_verified.boolean = True
    is_verified.short_description = 'Is Verified'
