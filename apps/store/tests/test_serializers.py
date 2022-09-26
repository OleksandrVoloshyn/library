from django.test import TestCase

from apps.store.models import BookModel
from apps.store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = BookModel.objects.create(name='book1', price=1000)
        book_2 = BookModel.objects.create(name='book2', price=100)
        data = BookSerializer((book_1, book_2), many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'book1',
                'price': '1000.00'
            },
            {
                'id': book_2.id,
                'name': 'book2',
                'price': '100.00'
            },
        ]
        self.assertEqual(expected_data, data)
