from functools import wraps
from django.shortcuts import redirect
from rest_framework import exceptions
from store.models import Product


def check_product_exist(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        if not Product.objects.filter(pk=kwargs['product_pk']).exists():
            raise exceptions.NotFound('Product not found')
        return func(request, *args, **kwargs)
    return wrap

def redirect_for_specific_method(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        if request.method == 'GET':
            if request.authenticators and not request.successful_authenticator:
                print('not authenticated')
                return redirect('/store')
            print('no permission')
            return redirect('/store/customers/me')
        return func(request, *args, **kwargs)
    return wrap
