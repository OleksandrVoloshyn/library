from django.contrib.auth.models import User
from django.db.models import Avg, Case, Count, When
from django.test import TestCase

from apps.store.models import BookModel, UserBookRelationModel
from apps.store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        user_1 = User.objects.create(username='user1', first_name='sasha', last_name='voloshyn')
        user_2 = User.objects.create(username='user2', first_name='ivan', last_name='test')
        user_3 = User.objects.create(username='user3', first_name='oleg', last_name='test2')

        book_1 = BookModel.objects.create(name='book1', price=1000, author_name='author1', owner=user_1)
        book_2 = BookModel.objects.create(name='book2', price=100, author_name='author2')

        UserBookRelationModel.objects.create(user=user_1, book=book_1, like=True, rate=5)
        UserBookRelationModel.objects.create(user=user_2, book=book_1, like=True, rate=5)
        user_book_3 = UserBookRelationModel.objects.create(user=user_3, book=book_1, like=True)
        user_book_3.rate = 4
        user_book_3.save()

        UserBookRelationModel.objects.create(user=user_1, book=book_2, like=True, rate=3)
        UserBookRelationModel.objects.create(user=user_2, book=book_2, like=True, rate=4)
        UserBookRelationModel.objects.create(user=user_3, book=book_2, like=False)

        books = BookModel.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelationmodel__like=True, then=1)))).order_by('id')
        data = BookSerializer(books, many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'book1',
                'price': '1000.00',
                'author_name': 'author1',
                'annotated_likes': 3,
                'rating': '4.67',
                'owner_name': 'user1',
                'readers': [
                    {'first_name': 'sasha', 'last_name': 'voloshyn'},
                    {'first_name': 'ivan', 'last_name': 'test'},
                    {'first_name': 'oleg', 'last_name': 'test2'}
                ]
            },
            {
                'id': book_2.id,
                'name': 'book2',
                'price': '100.00',
                'author_name': 'author2',
                'annotated_likes': 2,
                'rating': '3.50',
                'owner_name': '',
                'readers': [
                    {'first_name': 'sasha', 'last_name': 'voloshyn'},
                    {'first_name': 'ivan', 'last_name': 'test'},
                    {'first_name': 'oleg', 'last_name': 'test2'}
                ]
            },
        ]
        self.assertEqual(expected_data, data)
