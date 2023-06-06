"""Admin views."""
from django.contrib import admin

from taxi_manager.models import Car, CarOrder, Customer, Driver, Order


class CarInline(admin.TabularInline):
    """Inline admin class for displaying cars in the order admin panel."""

    model = CarOrder
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin class for managing orders in the admin panel."""

    readonly_fields = ['cost', 'rating', 'status']
    inlines = [CarInline]


admin.site.register(CarOrder)
admin.site.register(Driver)
admin.site.register(Customer)
admin.site.register(Car)
