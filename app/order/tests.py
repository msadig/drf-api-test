import random

from django.urls import reverse
from rest_framework import serializers, status
from rest_framework.test import APITestCase

from .models import Pizza, Order, OrderItem, Customer
from .api.serializers import PizzaSerializer, OrderSerializerBase, OrderReadSerializer, OrderItemReadSerializer
# Create your tests here.

FLAVORS = ("margarita", "marinara", "salami")


class PizzaViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        self.pizzas = [
            Pizza.objects.create(
                name=flavor
            ) for flavor in FLAVORS
        ]

    def test_pizza_list(self):
        list_url = reverse('order:pizza-list')
        queryset = Pizza.objects.all()
        response = self.client.get(list_url)
        serializer = PizzaSerializer(queryset, many=True)

        self.assertEqual(response.data.get('count'), len(queryset))
        self.assertEqual(response.data.get('results'), serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pizza_retrieve(self):
        pk = self.pizzas[0].id
        detail_url = reverse('order:pizza-detail', args=[pk, ])
        queryset = Pizza.objects.get(pk=pk)
        serializer = PizzaSerializer(queryset)
        response = self.client.get(detail_url)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OrderViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        self.pizzas = [
            Pizza.objects.create(
                name=flavor
            ) for flavor in FLAVORS
        ]
        self.orders = self.setup_dummy_orders()

    def setup_dummy_orders(self):
        orders = []
        for n in range(1, 5):
            customer = Customer.objects.create(
                full_name=f"John #{n}", email=f"john_{n}@example.com")
            order = Order.objects.create(customer=customer)
            for pizza in self.pizzas:
                OrderItem.objects.create(**{
                    "order": order,
                    "pizza": pizza,
                    "size": random.choice([x.value for x in OrderItem.Sizes]),
                    "count": random.randint(1, 5)
                })
            orders.append(order)

        return orders

    def test_order_list(self):
        list_url = reverse('order:order-list')
        queryset = Order.objects.all()
        serializer = OrderReadSerializer(queryset, many=True)
        response = self.client.get(list_url)

        self.assertEqual(response.data.get('count'), len(queryset))
        self.assertEqual(response.data.get('results'), serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_detail(self):
        pk = self.orders[0].id
        detail_url = reverse('order:order-detail', args=[pk])
        queryset = Order.objects.get(pk=pk)
        serializer = OrderReadSerializer(queryset)
        response = self.client.get(detail_url)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_orders_create(self):
        create_url = reverse('order:order-list')
        new_order_params = {
            "customer": {
                "full_name": "John Doe",
                "email": "john@example.com"
            },
            "items": [
                {
                    "pizza": pizza.id,
                    "size": random.choice([x.value for x in OrderItem.Sizes]),
                    "count": random.randint(1, 5)
                }
                for pizza in self.pizzas
            ],
        }
        response = self.client.post(
            create_url,
            data=new_order_params,
            format='json'
        )
        instance = Order.objects.get(pk=response.data.get('id'))
        serializer = OrderSerializerBase(instance)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_orders_update(self):
        pk = self.orders[0].id
        update_url = reverse('order:order-detail', args=[pk, ])
        update_order_params = {
            "status": Order.DeliveryStatuses.ACCEPTED.value
        }
        response = self.client.patch(
            update_url,
            data=update_order_params,
            format='json'
        )

        self.assertEqual(response.data.get("status"),
                         Order.DeliveryStatuses.ACCEPTED.value)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_orders_not_update(self):
        instance = self.orders[-1]
        instance.status = Order.DeliveryStatuses.DELIVERED
        instance.save(update_fields=['status'])

        update_url = reverse('order:order-detail', args=[instance.id, ])
        update_order_params = {
            "status": Order.DeliveryStatuses.ACCEPTED.value
        }
        response = self.client.patch(
            update_url,
            data=update_order_params,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

class OrderItemViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        self.pizzas = [
            Pizza.objects.create(
                name=flavor
            ) for flavor in FLAVORS
        ]
        self.orders = self.setup_dummy_orders()

    def setup_dummy_orders(self):
        orders = []
        for n in range(1, 5):
            customer = Customer.objects.create(
                full_name=f"John #{n}", email=f"john_{n}@example.com")
            order = Order.objects.create(customer=customer)
            for pizza in self.pizzas:
                OrderItem.objects.create(**{
                    "order": order,
                    "pizza": pizza,
                    "size": random.choice([x.value for x in OrderItem.Sizes]),
                    "count": random.randint(1, 5)
                })
            orders.append(order)

        return orders

    def test_order_items_list(self):
        instance = self.orders[1]
        order_items_list_url = reverse('order:order-items-list', kwargs={"order_id": instance.id})
        response = self.client.get(order_items_list_url)

        queryset = instance.orderitem_set.all()
        serializer = OrderItemReadSerializer(queryset, many=True)

        self.assertEqual(response.data.get('count'), len(queryset))
        self.assertEqual(response.data.get('results'), serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_order_items_update(self):
        order = self.orders[1]
        item = order.orderitem_set.first()

        order_items_update_url = reverse('order:order-items-detail', kwargs={
            "order_id": order.id,
            "pk": item.id,
        })
        update_order_params = {
            "count": 77
        }
        response = self.client.patch(
            order_items_update_url,
            data=update_order_params,
            format='json'
        )

        self.assertEqual(response.data.get('count'), 77)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_order_items_not_update(self):
        order = self.orders[-1]
        order.status = Order.DeliveryStatuses.DELIVERED
        order.save(update_fields=['status'])
        item = order.orderitem_set.first()

        order_items_update_url = reverse('order:order-items-detail', kwargs={
            "order_id": order.id,
            "pk": item.id,
        })
        update_order_params = {
            "count": 77
        }
        response = self.client.patch(
            order_items_update_url,
            data=update_order_params,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
