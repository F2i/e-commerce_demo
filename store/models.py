from django.db import models
from django.db.models import fields
from django.db.models.aggregates import Min
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, PROTECT, SET_NULL
from django.db.models.fields import related
from django.core.validators import FileExtensionValidator, MinValueValidator
from uuid import uuid4
from store.validators import FileSizeValidator
from django.conf import settings

from rest_framework import validators


# Promotion - Product many to many
class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount =  models.FloatField()


class Collection(models.Model):
    class Meta:
        ordering = ['title']

    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey('Product', on_delete=SET_NULL, null=True, related_name='+')
    
    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255) #varchar(255)
    slug = models.SlugField()
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=5, 
        decimal_places=1,
        validators=[MinValueValidator(1)]
    )
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=PROTECT)
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return self.title


class ProductImage(models.Model):
    class Utils:
        def get_product_title(instance, filename):
            return '/'.join(['store', f'{instance.product_id} - {instance.product}', filename])

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to=Utils.get_product_title,
        validators=[FileSizeValidator(max_file_size_mb=1)]
    )


class Customer(models.Model):
    MEMBER_SHIP_B = 'B'
    MEMBER_SHIP_S = 'S'
    MEMBER_SHIP_G = 'G'
    MEMBER_SHIP = [
        (MEMBER_SHIP_B, 'oc cho'),
        (MEMBER_SHIP_S, 'bac oc cho'),
        (MEMBER_SHIP_G, 'vang oc cho')
    ]
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, choices=MEMBER_SHIP, default=MEMBER_SHIP_B)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE)

    # Part1 - 4 - 5
    class Meta: 
        # db_table = 'store_customer'
        indexes = [
            models.Index(fields=['user'])
        ]
        ordering = ['user__first_name']

    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'


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

    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel order')
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=PROTECT, related_name='orderitem_set')
    product = models.ForeignKey(Product, on_delete=PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=5, decimal_places=1) # at the time we buy


class Adress(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)
    zip = models.SmallIntegerField()


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=CASCADE)
    product = models.ForeignKey(Product, on_delete=CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = [['cart', 'product']]


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

