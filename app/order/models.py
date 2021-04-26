from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Create your models here.


class Pizza(models.Model):
    # information
    name = models.CharField(max_length=128)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", )

    def __str__(self) -> str:
        return str(self.name)


class Customer(models.Model):
    # information
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        blank=True, null=True,
        help_text=_(
            'Store user reference if order placed by an authenticated user')
    )
    name = models.CharField(max_length=128)
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", )

    def __str__(self) -> str:
        return str(self.name)


class Order(models.Model):
    class DeliveryStatuses(models.TextChoices):
        NEW = 'NEW', _('New order placed')
        ACCEPTED = 'ACCEPTED', _('Order accepted by restaurant')
        READY = 'READY', _('Order ready for delivery')
        SHIPPED = 'SHIPPED', _('Order on its way to customer')
        DELIVERED = 'DELIVERED', _('Delivered')

    # relations
    customer = models.ForeignKey(
        'Customer', on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField('Pizza', through='OrderItem')

    # information
    status = models.CharField(max_length=10, choices=DeliveryStatuses.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", )

    def __str__(self) -> str:
        return f"{self.customer}'s Order ({self.status})"


class OrderItem(models.Model):
    class Sizes(models.TextChoices):
        SMALL = 'S', _('Small')
        MEDIUM = 'M', _('Medium')
        LARGE = 'L', _('Large')

    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    pizza = models.ForeignKey('Pizza', on_delete=models.CASCADE)
    size = models.CharField(choices=Sizes.choices, max_length=6)
    count = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f'{self.order}: {self.pizza} - {self.size} ({self.count})'
