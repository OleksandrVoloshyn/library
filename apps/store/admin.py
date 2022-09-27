from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.store.models import BookModel


@admin.register(BookModel)
class BookAdmin(ModelAdmin):
    pass
