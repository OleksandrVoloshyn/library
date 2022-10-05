from django.contrib.auth.models import User
from django.test import TestCase

from apps.store.models import BookModel, UserBookRelationModel
from apps.store.services import set_rating


class SetRatingTestCase(TestCase):
    def setUp(self):
        user_1 = User.objects.create(username='user1', first_name='sasha', last_name='voloshyn')
        user_2 = User.objects.create(username='user2', first_name='ivan', last_name='test')
        user_3 = User.objects.create(username='user3', first_name='oleg', last_name='test2')

        self.book_1 = BookModel.objects.create(name='book1', price=1000, author_name='author1', owner=user_1)

        UserBookRelationModel.objects.create(user=user_1, book=self.book_1, like=True, rate=5)
        UserBookRelationModel.objects.create(user=user_2, book=self.book_1, like=True, rate=5)
        UserBookRelationModel.objects.create(user=user_3, book=self.book_1, like=True, rate=4)

    def test_ok(self):
        set_rating(self.book_1)
        self.book_1.refresh_from_db()
        self.assertEqual('4.67', str(self.book_1.rating))
