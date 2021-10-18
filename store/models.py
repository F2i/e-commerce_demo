from django.db import models
from django.db.models.aggregates import Min
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, PROTECT, SET_NULL


# Promotion - Product many to many
class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount =  models.FloatField()


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey('Product', on_delete=SET_NULL, null=True, related_name='+')


class Product(models.Model):
    # sku = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=255) #varchar(255)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=1)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=PROTECT)
    promotions = models.ManyToManyField(Promotion)


class Customer(models.Model):
    MEMBER_SHIP_B = 'B'
    MEMBER_SHIP_S = 'S'
    MEMBER_SHIP_G = 'G'
    MEMBER_SHIP = [
        (MEMBER_SHIP_B, 'oc cho'),
        (MEMBER_SHIP_S, 'bac oc cho'),
        (MEMBER_SHIP_G, 'vang oc cho')
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birthday = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBER_SHIP, default=MEMBER_SHIP_B)


class Order(models.Model):
    STATUS_P = 'P'
    STATUS_C = 'C'
    STATUS_F = 'F'
    PAYMENT_STATUS = [
        (STATUS_P, 'dang cho thanh toan'),
        (STATUS_C, 'tra tien roi'),
        (STATUS_F, 'du me web ngu')
    ]
    paymentstatus = models.CharField(max_length=1, choices=PAYMENT_STATUS, default=STATUS_P)
    placed_at = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=PROTECT)
    product = models.ForeignKey(Product, on_delete=PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=5, decimal_places=1) # at the time we buy


class Adress(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=CASCADE)
    product = models.ForeignKey(Product, on_delete=CASCADE)
    quantity = models.PositiveSmallIntegerField()


