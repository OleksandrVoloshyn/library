from django.db.models import Avg, Case, Count, When

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import BookModel, UserBookRelationModel
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import BookSerializer, UserBookRelatedSerializer


class BookViewSet(ModelViewSet):
    queryset = BookModel.objects.all().annotate(
        annotated_likes=Count(Case(When(userbookrelationmodel__like=True, then=1)))).select_related(
        'owner').prefetch_related('readers').order_by('id')
    serializer_class = BookSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('price',)
    search_fields = ('name', 'author_name')
    ordering_fields = ('price',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UserBookRelationViewSet(GenericViewSet, UpdateModelMixin):
    permission_classes = (IsAuthenticated,)
    queryset = UserBookRelationModel.objects.all()
    serializer_class = UserBookRelatedSerializer
    lookup_field = 'book'

    def get_object(self):
        obj, _ = UserBookRelationModel.objects.get_or_create(user=self.request.user, book_id=self.kwargs['book'])
        return obj
