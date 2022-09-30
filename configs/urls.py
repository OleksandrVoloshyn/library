from django.contrib import admin
from django.urls import include, path

from rest_framework.routers import SimpleRouter

from apps.store.views import BookViewSet, UserBookRelationViewSet

router = SimpleRouter()

router.register('books', BookViewSet, basename='books')
router.register('book_relations', UserBookRelationViewSet, basename='book_relations')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls'))
]

urlpatterns += router.urls
