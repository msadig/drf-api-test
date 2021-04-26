from django.contrib import admin
from order import models


# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    extra = 0  # how many rows to show


@admin.register(models.Pizza)
class PizzaAdmin(admin.ModelAdmin):
    pass

# Register your models here.


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline,
    ]
    list_display = [
        '__str__',
        'customer',
        'status',
        'created_at',
    ]
