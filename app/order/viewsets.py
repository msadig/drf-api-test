from rest_framework.viewsets import ModelViewSet

from .models import Order
from .serializers import OrderSerializer


class OrderViewset(ModelViewSet):
    model = Order
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
