from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.store.models import BookModel
from apps.store.serializers import BookSerializer


class BookViewSet(ModelViewSet):
    queryset = BookModel.objects.all()
    serializer_class = BookSerializer
    # permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('price',)
    search_fields = ('name', 'author_name')
    ordering_fields = ('price',)
