from django.db.models.expressions import F
from django.http.request import QueryDict
from django.http.response import HttpResponse
from django.urls.base import resolve, reverse
from django.utils.datastructures import MultiValueDict
from django.utils.functional import empty
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from rest_framework import exceptions, mixins, pagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import override_method
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView

from store.exceptions import PermissonDeniedException
from . import decorators
# from django.core import urlresolvers

from .permissions import IsAdminOrReadOnly
from .pagination import DefaultPagination
from .filters import ProductFilter
from .models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product, ProductImage, Review
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CreateCustomerSerializer, CreateOrderSerializer, CustomerSerializer, OrderItemSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateCustomerSerializer, UpdateOrderSerializer
from store import models

from store import serializers

from store import permissions



class ProductViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Product.objects.select_related('collection').prefetch_related('productimage_set').order_by('id')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly,]
    search_fields = ['title', 'description', 'collection__title']
    ordering_fields = ['id']


    def get_serializer_context(self):
        return {'request':self.request}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.orderitem_set.count() > 0:
            return Response(
                {'error':'Cannot deleted cuz Proteced from Product'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('product')).order_by('id')
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly,]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.product_set.count() > 0:
            return Response(
                {'error':'Cannot deleted cuz Proteced from Collection'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(decorators.check_product_exist, name='list')
@method_decorator(decorators.check_product_exist, name='retrieve')
@method_decorator(decorators.check_product_exist, name='create')
@method_decorator(decorators.check_product_exist, name='update')
@method_decorator(decorators.check_product_exist, name='destroy')
class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    serializer_class_model = serializer_class.Meta.model
    queryset = serializer_class_model.objects.all()
    
    def get_queryset(self):
        return Review.objects.filter(product=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    http_method_rel_serializer = {
        'GET': CartItemSerializer,
        'POST': AddCartItemSerializer,
        'PATCH': UpdateCartItemSerializer
    }
    queryset = CartItem.objects.select_related('product').order_by('id')
    
    def get_serializer_class(self):
        self.serializer_class = self.http_method_rel_serializer.get(self.request.method, CartItemSerializer)
        return super().get_serializer_class()

    def get_queryset(self):
        return super().get_queryset().filter(cart=self.kwargs['cart_pk'])

    def get_serializer_context(self):
        return {**super().get_serializer_context(), **{'cart_id':self.kwargs['cart_pk']}}

    
class CartViewSet(
                mixins.CreateModelMixin,
                mixins.RetrieveModelMixin,
                mixins.DestroyModelMixin,
                GenericViewSet
            ):
    queryset = Cart.objects.prefetch_related('cartitem_set__product').order_by('id')
    serializer_class = CartSerializer


class CustomerViewSet(ModelViewSet):
    http_method_rel_serializer ={
        'GET': CustomerSerializer,
        'POST': CreateCustomerSerializer,
        'PUT': UpdateCustomerSerializer,
        'PATCH': UpdateCustomerSerializer,
    }
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser,]
    redirect_view_name = ''
    
    def list(self, request, *args, **kwargs):
        if self.redirect_view_name:
            return redirect(self.redirect_view_name)
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        self.serializer_class = self.http_method_rel_serializer.get(self.request.method, CustomerSerializer)
        return super().get_serializer_class()

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated,])
    def me(self, request):
        (customer, created) = Customer.objects.select_related('user').get_or_create(user_id=request.user.id)
        serializer = self.get_serializer_class()(customer)
        def get():
            # print(resolve(request.path_info))
            return

        def put():
            serializer.initial_data = request.data
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return
        
        http_method_to_function_dict = {
            'GET': get,
            'PUT': put,
        }

        http_method_to_function_dict[request.method]()
        return Response(serializer.data)

    def permission_denied(self, request, message=None, code=None):
        if request.method == 'GET':
            if request.authenticators and not request.successful_authenticator:
                self.redirect_view_name = 'store/'
            else:
                self.redirect_view_name = 'store:customer-me'
            return
        return super().permission_denied(request, message=message, code=code)

 
class OrderItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    http_method_rel_serializer = {
        'GET': OrderItemSerializer,
        'POST': OrderItemSerializer,
        'PATCH': OrderItemSerializer
    }
    queryset = OrderItem.objects.select_related('product').order_by('id')
    
    def get_serializer_class(self):
        self.serializer_class = self.http_method_rel_serializer.get(self.request.method, OrderItemSerializer)
        return super().get_serializer_class()

    def get_queryset(self):
        return super().get_queryset().filter(order=self.kwargs['order_pk'])

    def get_serializer_context(self):
        return {**super().get_serializer_context(), **{'order_id':self.kwargs['order_pk']}}

    
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related('orderitem_set__product').order_by('id')
    serializer_class = OrderSerializer
    switch_serializer_class = True
    permission_classes = [IsAdminUser,]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method not in ['PATCH', 'DELETE']:
            return [IsAuthenticated(),]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'POST' and self.switch_serializer_class:
            return CreateOrderSerializer
        if self.request.method == 'PATCH' and self.switch_serializer_class:
            return UpdateOrderSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if not self.request.user.is_staff:
            return super().get_queryset().annotate(user_id=F('customer__user__id')).filter(user_id=self.request.user.id)
        return super().get_queryset()

    def create(self, request, *args, **kwargs):
        try:
            customer_id = Customer.objects.get(user_id=self.request.user.id).id
        except Customer.DoesNotExist:
            # should raise exceptions.ValidationError instead
            return Response({'error':'Customer id not found'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_id = serializer.validated_data['cart_id']

        if not Cart.objects.filter(pk=cart_id).exists():
            return Response({'error':'Cart id not found'}, status=status.HTTP_400_BAD_REQUEST)
        if Cart.objects.filter(pk=cart_id).count() == 0:
            return Response({'error':'Empty cart'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderSerializer(
            data=request.data,
            context={
                **serializer.context,
                **{'cart_id': cart_id}
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['customer_id'] = customer_id
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


@method_decorator(decorators.check_product_exist, name='list')
@method_decorator(decorators.check_product_exist, name='retrieve')
@method_decorator(decorators.check_product_exist, name='create')
@method_decorator(decorators.check_product_exist, name='update')
@method_decorator(decorators.check_product_exist, name='destroy')
class ProductImageView(ModelViewSet):
    queryset = ProductImage.objects.select_related('product').order_by('id')
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return super().get_queryset().filter(product=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {**super().get_serializer_context(), **{'product_id':self.kwargs['product_pk']}}



"""
"""
"""
                                                FOR REVIEW
"""
"""
"""
#function based view
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        qset = Product.objects.select_related('collection').all().order_by('id')[:5]
        product_serializer = ProductSerializer(qset, many=True, context={'request':request})
        return Response(product_serializer.data)
    elif request.method == 'POST':
        product_serializer = ProductSerializer(data=request.data, context={'request':request})
        product_serializer.is_valid(raise_exception=True)
        product_serializer.save()
        return Response(product_serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailAPIView(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        product_serializer = ProductSerializer(product, context={'request':request})
        return Response(product_serializer.data)

    def patch(self, request, id):
        product = get_object_or_404(Product, pk=id)
        product_serializer = ProductSerializer(product, data=request.data, context={'request':request}, partial=True)
        product_serializer.is_valid(raise_exception=True)
        product_serializer.save()
        return Response(product_serializer.data, status=status.HTTP_202_ACCEPTED)

    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if product.orderitem_set.count() > 0:
            return Response({'error':'Cannot deleted cuz'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_202_ACCEPTED)


class ProductDetailGenericView(RetrieveUpdateDestroyAPIView):
    lookup_field='id'
    queryset = Product.objects.select_related('collection')
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {'request':self.request}
