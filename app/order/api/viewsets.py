from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.exceptions import NotAcceptable
from rest_framework import filters
from rest_framework_extensions.mixins import NestedViewSetMixin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


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


@method_decorator(name='list', decorator=swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'status', openapi.IN_QUERY,
            description=_("Filter orders by status"),
            type=openapi.TYPE_STRING,
            enum=[x.value for x in Order.DeliveryStatuses]
        ),
        openapi.Parameter(
            'search', openapi.IN_QUERY,
            description=_("Search for given customer's orders"),
            type=openapi.TYPE_STRING
        )
    ]
))
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
    filter_backends = [filters.SearchFilter]
    search_fields = ['customer__full_name', 'customer__email']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status', None)

        if status:
            queryset = queryset.filter(status=status)

        return queryset

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
