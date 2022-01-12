from django.core import exceptions
from django.core.mail.message import BadHeaderError
from django.db.models.expressions import Case, Col, Func, OuterRef, Ref, When
from django.db.models.fields import IntegerField
from django.db.models.query_utils import FilteredRelation
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Count
from django.contrib.contenttypes.models import ContentType
from .tasks import notify_customers
from store.models import Collection, Customer, Product, OrderItem, Order, Review
from store.views import CustomerViewSet
from tags.models import TaggedItem

from django.core.mail import EmailMessage, send_mail, mail_admins
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from templated_mail.mail import BaseEmailMessage

from rest_framework.views import APIView
import requests

# Create your views here.

def say_hello(request):
    # try:
    #     # send_mail('subject', 'nhan danh cong ly du ma may', 'info@meme.com', ['nhadanhcongly@gmail.xxx',])
    #     # mail_admins('subject', 'nhan danh cong ly du ma may', html_message='<a href="https://google.com">meme</a>')
    #     email = BaseEmailMessage(
    #         template_name='emails/email.html',
    #         context={
    #             'name': 'Yo excuse me wtf',
    #         }
    #     ) 
    #     email.attach_file('playMeme/static/images/long_vuong_phu_ho.png')
    #     email.send(to=['nghesinhandan@gmail.cc', 'dumemay@gmail.cc'])
    # except BadHeaderError:
    #     return redirect('store/')
    notify_customers.delay('Du ma m')
    return HttpResponse('nhan danh cong ly du ma may')

@method_decorator(cache_page(1*60), name='get')
class HelloView(APIView):
    def get(self, request):
        response = requests.get('https://httpbin.org/delay/2')
        data = response.json()
        return HttpResponse(data)
        