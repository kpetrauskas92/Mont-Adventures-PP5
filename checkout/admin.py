from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Order, OrderLineItem


class OrderLineItemAdminInline(admin.TabularInline):
    """
    Inline admin class for the OrderLineItem model. This inline class
    allows us to edit line items directly within the Order model interface.
    """
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)
    fields = (('trip', 'available_date'),
              'guests', ('status'))
    extra = 0


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    """
    Admin class for the Order model. This class defines how the Order model
    should be displayed and managed in the Django admin interface.
    """
    inlines = (OrderLineItemAdminInline,)
    readonly_fields = ('order_number', 'order_total', 'grand_total')

    fields = ('order_number', 'user_profile', 'first_name',
              'last_name', 'email',
              'order_total', 'grand_total', 'stripe_pid')

    list_display = ('order_number', 'first_name',
                    'last_name', 'order_total', 'grand_total', 'is_canceled')

    ordering = ('-order_number',)

    def is_canceled(self, obj):
        return all(
            lineitem.status == 'canceled' for lineitem in obj.lineitems.all())
    is_canceled.boolean = True
    is_canceled.admin_order_field = 'lineitems__status'
    is_canceled.short_description = 'Is Canceled ?'
