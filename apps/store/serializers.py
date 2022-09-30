from django.contrib.auth.models import User

from rest_framework.serializers import CharField, DecimalField, IntegerField, ModelSerializer

from .models import BookModel, UserBookRelationModel


class BookReaderSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BookSerializer(ModelSerializer):
    # likes_count = SerializerMethodField()
    annotated_likes = IntegerField(read_only=True)
    rating = DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = CharField(source='owner.username', default='', read_only=True)
    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = BookModel
        fields = ('id', 'name', 'price', 'author_name', 'annotated_likes', 'rating', 'owner_name', 'readers')

    # @staticmethod
    # def get_likes_count(instance):
    #     return UserBookRelationModel.objects.filter(book=instance, like=True).count()


class UserBookRelatedSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelationModel
        fields = ('book', 'like', 'in_bookmarks', 'rate')
