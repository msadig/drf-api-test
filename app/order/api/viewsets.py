from django.utils.translation import gettext_lazy as _

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.exceptions import NotAcceptable
from rest_framework_extensions.mixins import NestedViewSetMixin


from order.models import Order, Pizza, OrderItem
from .serializers import (
    OrderSerializerBase,
    OrderReadSerializer,
    OrderUpdateSerializer,
    PizzaSerializer,
    OrderItemSerializerBase,
    OrderItemReadSerializer,
)
from .mixins import MultiSerializerViewSetMixin


class OrderViewSet(MultiSerializerViewSetMixin, NestedViewSetMixin, ModelViewSet):
    model = Order
    queryset = Order.objects.all()
    serializer_classes = {
        "default": OrderSerializerBase,
        "list": OrderReadSerializer,
        "retrieve": OrderReadSerializer,
        "update": OrderUpdateSerializer,
        "partial_update": OrderUpdateSerializer,
    }

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status in Order.UNEDITABLE_STATUES:
            raise NotAcceptable(
                detail=_('You can not change orders with the status %s' %
                         instance.status)
            )

        return super().update(request, *args, **kwargs)


class OrderItemViewSet(MultiSerializerViewSetMixin, NestedViewSetMixin, ModelViewSet):
    model = OrderItem
    queryset = OrderItem.objects.all()
    serializer_classes = {
        "default": OrderItemSerializerBase,
        "list": OrderItemReadSerializer,
        "retrieve": OrderItemReadSerializer,
    }

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.order.status in Order.UNEDITABLE_STATUES:
            raise NotAcceptable(
                detail=_('You can not change orders with the status %s' %
                         instance.order.status)
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.order.status in Order.UNEDITABLE_STATUES:
            raise NotAcceptable(
                detail=_('You can not change orders with the status %s' %
                         instance.order.status)
            )
        return super().destroy(request, *args, **kwargs)


class PizzaViewSet(ReadOnlyModelViewSet):
    model = Pizza
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer
