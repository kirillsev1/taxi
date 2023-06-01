from django.contrib import admin
from taxi_manager.models import Car, CarOrder, Customer, Driver, Order


class CarInline(admin.TabularInline):
    model = CarOrder
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['cost', 'rating', 'status']
    inlines = [CarInline]


admin.site.register(CarOrder)
admin.site.register(Driver)
admin.site.register(Customer)
admin.site.register(Car)
