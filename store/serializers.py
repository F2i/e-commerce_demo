from django.db.models.expressions import F, OuterRef
from django.db.models.query import QuerySet
from django.http.response import Http404, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.db import transaction
from rest_framework import serializers, status
from decimal import Decimal
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.fields import empty

from rest_framework.permissions import OR
from rest_framework.response import Response

from store.models import Cart, CartItem, Customer, Order, OrderItem, Product, Collection, ProductImage, Promotion, Review
from .signals import order_created

class SpecificPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.pk_kw = kwargs.pop('pk_kw', None)
        super().__init__(**kwargs)
    
    def get_queryset(self):
        return super().get_queryset().filter(pk=self.context['request'].parser_context['kwargs'][self.pk_kw])

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']
    
    product_count = serializers.IntegerField(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def create(self, validated_data):
        validated_data['product_id'] = self.context['product_id']
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'unit_price', 'inventory', 'collection', 'price_with_tax', 'productimage_set']

    productimage_set = ProductImageSerializer(many=True, read_only=True)
    price_with_tax = serializers.SerializerMethodField(read_only=True, method_name='price_with_tax_method')
    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(),
        view_name='store:collection-detail',
    )

    def price_with_tax_method(self, product: Product):
        return Decimal(product.unit_price * Decimal(1.05))  

    def validate(self, attrs):
        return super().validate(attrs)
        # if attrs['pw'] != attrs['confirmed_pw']:
        #     return serializers.ValidationError('Password not match')

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'title', 'description', 'date', 'product']

    product = serializers.PrimaryKeyRelatedField(read_only = True)

    def create(self, validated_data):
        validated_data['product_id'] = self.context['product_id']
        return super().create(validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'cart_item_total_price']
    
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    cart_item_total_price = serializers.SerializerMethodField(
        read_only=True,
        method_name='cart_item_total_price_method'
    )

    def cart_item_total_price_method(self, cartitem: CartItem):
        return Decimal(cartitem.product.unit_price * cartitem.quantity)


class AddCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']
    
    product_id = serializers.IntegerField(min_value=1)

    def save(self, **kwargs):
        self.validated_data['cart_id'] = self.context['cart_id']
        try:
            self.instance = CartItem.objects.get(
                cart_id=self.validated_data['cart_id'],
                product_id=self.validated_data['product_id']
            )
            # front-end send new 'POST'
            self.validated_data['quantity'] += self.instance.quantity
        except CartItem.DoesNotExist:
            pass
        return super().save(**kwargs)


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'cartitem_set', 'cart_total_price']

    id = serializers.CharField(read_only=True)
    cartitem_set = CartItemSerializer(CartItem.objects.all(), many=True, read_only=True)
    cart_total_price = serializers.SerializerMethodField(
        read_only=True,
        method_name='cart_total_price_method'
    )

    def cart_total_price_method(self, cart: Cart):
        return Decimal(sum(cartitem.product.unit_price * cartitem.quantity for cartitem in cart.cartitem_set.all()))


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']


class CreateCustomerSerializer(CustomerSerializer):
    user_id = serializers.IntegerField(min_value=1, read_only=False)
    

class UpdateCustomerSerializer(CustomerSerializer):
    user_id = serializers.IntegerField(min_value=1, read_only=True)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'order_item_total_price']
    
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    order_item_total_price = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_order_item_total_price'
    )

    def get_order_item_total_price(self, orderitem: OrderItem):
        return Decimal(orderitem.product.unit_price * orderitem.quantity)


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer_id', 'placed_at', 'paymentstatus', 'orderitem_set', 'order_total_price']

    id = serializers.CharField(read_only=True)
    paymentstatus = serializers.CharField(read_only=True)
    customer_id = serializers.IntegerField(read_only=True)
    orderitem_set = OrderItemSerializer(OrderItem.objects.all(), many=True, read_only=True)
    order_total_price = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_order_total_price'
    )

    def get_order_total_price(self, order: Order):
        return Decimal(sum((orderitem.product.unit_price * orderitem.quantity) for orderitem in order.orderitem_set.all()))
    
    def save(self, **kwargs):
        with transaction.atomic():
            order = super().save(**kwargs)
            if self.context['request'].method == 'POST':
                cartitem_set = CartItem.objects.select_related('product').filter(cart_id=self.context['cart_id'])
                orderitem_set = [
                    OrderItem(
                        order=order,
                        product=item.product,
                        unit_price=item.product.unit_price,
                        quantity=item.quantity
                    ) for item in cartitem_set
                ]
                OrderItem.objects.bulk_create(orderitem_set)
                order_created.send_robust(sender=self.__class__, order=order.id)
                # Cart.objects.filter(pk=self.context['cart_id']).delete()
            else:
                pass
            return order
        

class CreateOrderSerializer(OrderSerializer):
    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ['cart_id']

    cart_id = serializers.UUIDField()


class UpdateOrderSerializer(OrderSerializer):
    paymentstatus = serializers.CharField(read_only=False)
