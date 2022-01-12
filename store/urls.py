from django.urls import path, include
from django.urls.resolvers import URLPattern
from . import views
from rest_framework_nested import routers
from pprint import pprint

app_name = 'store'

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'collections', views.CollectionViewSet)
router.register(r'carts', views.CartViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'customers', views.CustomerViewSet)
products_router=routers.NestedDefaultRouter(router, r'products', lookup=r'product')
products_router.register(r'reviews', views.ReviewViewSet, basename=r'product-review')
products_router.register(r'images', views.ProductImageView, basename=r'product-image')
cartitems_router=routers.NestedDefaultRouter(router, r'carts', lookup=r'cart')
cartitems_router.register(r'cartitems', views.CartItemViewSet, basename=r'cart-cartitem')
oderitems_router=routers.NestedDefaultRouter(router, r'orders', lookup=r'order')
oderitems_router.register(r'orderitems', views.OrderItemViewSet, basename=r'order-Oderitem')
# pprint(products_router.urls)

urlpatterns = [
    path(str(), include(router.urls)),
    path(str(), include(products_router.urls)),
    path(str(), include(cartitems_router.urls)),
    path(str(), include(oderitems_router.urls)),
]
