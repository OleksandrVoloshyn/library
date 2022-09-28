from rest_framework.serializers import ModelSerializer

from .models import BookModel


class BookSerializer(ModelSerializer):
    class Meta:
        model = BookModel
        fields = ('id', 'name', 'price', 'author_name')
