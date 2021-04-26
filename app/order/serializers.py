from itertools import groupby

from rest_framework import serializers

from .models import Order, Customer, OrderItem, Pizza


class PizzaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pizza
        fields = [
            "id",
            "name",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


class OrderItemSerializerBase(serializers.ModelSerializer):
    count = serializers.IntegerField(min_value=1)
    # pizza = serializers.PrimaryKeyRelatedField(queryset=Pizza.objects.all())

    class Meta:
        model = OrderItem
        fields = [
            "pizza",
            "size",
            "count",
        ]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "full_name",
            "email",
        ]


class OrderSerializerBase(serializers.ModelSerializer):
    customer = CustomerSerializer()
    items = OrderItemSerializerBase(many=True, source='orderitem_set')

    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def create_customer(self, validated_data):
        customer_serializer = CustomerSerializer(data=validated_data)
        customer_serializer.is_valid(raise_exception=True)
        customer = customer_serializer.save()
        return customer

    def create_order_items(self, validated_data, order_instance):
        """Group items by size to calculate the quantity
        """
        for size, items in groupby(validated_data, key=lambda x: x['size']):
            grouped_item = list(items)
            qty = sum(i['count'] for i in grouped_item)
            item_serializer = OrderItemSerializerBase(data={
                "pizza": grouped_item[0]['pizza'].pk,
                "count": qty,
                "size": size,
            })
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save(order_id=order_instance.pk)

    def create(self, validated_data):
        customer = validated_data.pop('customer')
        items = validated_data.pop('orderitem_set')
        validated_data['status'] = Order.DeliveryStatuses.NEW
        validated_data['customer'] = self.create_customer(customer)
        order_instance = super().create(validated_data)

        self.create_order_items(items, order_instance)
        return order_instance


class OrderItemReadSerializer(OrderItemSerializerBase):
    pizza = PizzaSerializer(read_only=True)

    class Meta(OrderItemSerializerBase.Meta):
        pass


class OrderReadSerializer(OrderSerializerBase):
    items = OrderItemReadSerializer(many=True, source='orderitem_set')
    pass
