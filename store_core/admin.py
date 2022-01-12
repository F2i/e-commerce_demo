from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models.expressions import OuterRef
from store import models
from store.admin import ProductAdmin
from store.models import Product
from tags.models import Tag, TaggedItem
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name'),
        }),
    )
    pass


class TagInline(GenericTabularInline):
    model = TaggedItem
    autocomplete_fields = ['tag']
    extra = 0


class CustomProductAdmin(ProductAdmin):
    inlines = ProductAdmin.inlines + [TagInline]
    list_display = ProductAdmin.list_display + ['label']

    @admin.display(ordering='label')
    def label(self, product):
        return product.label

    def get_queryset(self, request):
        # x = super().get_queryset(request).annotate(label=TaggedItem.objects.get_t_for(Product, OuterRef('id')))
        # print(x.query)
        return super().get_queryset(request).annotate(label=TaggedItem.objects.get_t_for(Product, OuterRef('id')))


admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)