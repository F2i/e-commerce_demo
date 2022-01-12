from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'label']
    ordering = ['id']
    search_fields = ['label']