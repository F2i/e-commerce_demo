import re
from typing import ClassVar
from django import contrib
from django.contrib import admin, messages
from django.contrib.admin.decorators import action
from django.contrib.contenttypes.models import ContentType
from django.db.models.aggregates import Count
from django.db.models.expressions import OuterRef, Ref, Subquery, Value, RawSQL
from django.db.models.fields import Field
from django.db.models.query import QuerySet
from django.contrib.contenttypes.admin import GenericTabularInline
from django.db.models import Q, F, Count, Case, When
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    ordering = ['title']
    list_per_page = 20
    search_fields = ['title']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (reverse('admin:store_product_changelist')
            + '?'
            + urlencode(
                {'collection__id': str(collection.id)}
            )
        )
        return format_html('<a href="{}">{}</a>', url, collection.products_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('product'))


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'
    LOW_INVENTORY = '<10'
    HIGH_INVENTORY = '>50'
    def lookups(self, request, model_admin):
        return [
            (self.LOW_INVENTORY, 'Low'),
            (self.HIGH_INVENTORY, 'Nhieu'),
        ]  

    def queryset(self, request, queryset: QuerySet):
        if self.value() == self.LOW_INVENTORY:
            return queryset.filter(inventory__lt=10)
        elif self.value() == self.HIGH_INVENTORY:
            return queryset.filter(inventory__gt=50)


@admin.register(models.Customer)
class CustomernAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'memebership_status', 'orders_count']
    ordering = ['id']
    list_per_page = 20
    search_fields = ['full_name__istartswith']
    list_filter = ['membership']
    autocomplete_fields = ['user']

    @admin.display(ordering='membership')
    def memebership_status(self, customer):
        if customer.membership == 'B':
            return 'Bronze'
        elif customer.membership == 'S':
            return 'Silver'
        return 'Gold'

    @admin.display(ordering='user__first_name')
    def full_name(self, customer):
        return f'{customer.user.first_name} {customer.user.last_name}'

    @admin.display(ordering='orders_count')
    def orders_count(self, customer):
        url = (reverse('admin:store_order_changelist')
            + '?'
            + urlencode(
                {'customer__id': str(customer.id)}
            ))
        return format_html('<a href="{}">{}</a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count('order'))


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer_fullname', 'orderitems_count', 'status_of_payment']
    inlines = [OrderItemInline]
    ordering = ['id']
    list_per_page = 20
    exclude = ['placed_at']

    @admin.display(ordering='customer')
    def customer_fullname(self, order):
        return order.customer

    @admin.display(ordering='orderitems_count')
    def orderitems_count(self, order):
        return order.orderitems_count

    @admin.display(ordering='status_of_payment')
    def status_of_payment(self, order):
        return order.status_of_payment

    def get_queryset(self, request) :
        return super().get_queryset(request).annotate(orderitems_count=Count('orderitem')
            , status_of_payment=F('paymentstatus'))


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']
    extra = 0

    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail"/>')

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    autocomplete_fields = ['collection']
    prepopulated_fields = {
        'slug':['title'],
    }
    actions = ['clear_inventory']
    list_display = ['id', 'title', 'inventory', 'collection']
    list_editable = ['inventory']
    list_filter = [InventoryFilter, 'collection']
    list_per_page = 20
    ordering = ['id']
    search_fields = ['title']

    @admin.action(description='Clear Inventory')
    def clear_inventory(self, request, queryset: QuerySet):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} product(s) updated',
            messages.SUCCESS
        )

    class Media:
        css = {
            'all': ['store/styles.css']
        }
