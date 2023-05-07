from django.contrib import admin

from .models import Driver, Customer, Car, Order, CarOrder


# Register your models here.
@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    ...


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    ...


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    ...


class CarInline(admin.TabularInline):
    model = CarOrder
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['cost', 'rating', 'status']
    inlines = [CarInline]


admin.site.register(CarOrder)
