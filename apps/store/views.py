from rest_framework.viewsets import ModelViewSet

from apps.store.models import BookModel
from apps.store.serializers import BookSerializer


class BookViewSet(ModelViewSet):
    queryset = BookModel.objects.all()
    serializer_class = BookSerializer
