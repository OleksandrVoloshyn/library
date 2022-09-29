from rest_framework.serializers import DecimalField, IntegerField, ModelSerializer, SerializerMethodField

from .models import BookModel, UserBookRelationModel


class BookSerializer(ModelSerializer):
    likes_count = SerializerMethodField()
    annotated_likes = IntegerField(read_only=True)
    rating = DecimalField(max_digits=3, decimal_places=2, read_only=True)

    class Meta:
        model = BookModel
        fields = ('id', 'name', 'price', 'author_name', 'likes_count', 'annotated_likes', 'rating')

    @staticmethod
    def get_likes_count(instance):
        return UserBookRelationModel.objects.filter(book=instance, like=True).count()


class UserBookRelatedSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelationModel
        fields = ('book', 'like', 'in_bookmarks', 'rate')
