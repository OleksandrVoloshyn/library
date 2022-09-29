from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.store.models import BookModel, UserBookRelationModel


@admin.register(BookModel)
class BookAdmin(ModelAdmin):
    pass


@admin.register(UserBookRelationModel)
class UserBookRelationAdmin(ModelAdmin):
    pass
