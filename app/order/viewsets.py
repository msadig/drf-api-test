from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Order, Pizza
from .serializers import (
    OrderSerializerBase,
    OrderReadSerializer,
    PizzaSerializer
)
from .mixins import MultiSerializerViewSetMixin


class OrderViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    model = Order
    queryset = Order.objects.all()
    serializer_classes = {
        "default": OrderSerializerBase,
        "list": OrderReadSerializer,
        "retrieve": OrderReadSerializer,
    }


class PizzaViewSet(ReadOnlyModelViewSet):
    model = Pizza
    queryset = Pizza.objects.all()
    serializer_class = PizzaSerializer
