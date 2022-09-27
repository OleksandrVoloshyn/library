from django.contrib import admin
from django.urls import path

from rest_framework.routers import SimpleRouter

from apps.store.views import BookViewSet

router = SimpleRouter()

router.register('books', BookViewSet, basename='books')

urlpatterns = [
    path('admin/', admin.site.urls)
]

urlpatterns += router.urls
