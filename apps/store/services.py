from django.db.models import Avg

from .models import UserBookRelationModel


def set_rating(book):
    rating = UserBookRelationModel.objects.filter(book=book).aggregate(rating=Avg('rate')).get('rating')
    book.rating = rating
    book.save()
