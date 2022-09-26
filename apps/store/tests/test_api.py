from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.store.models import BookModel
from apps.store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def test_get(self):
        book_1 = BookModel.objects.create(name='book1', price=1000)
        book_2 = BookModel.objects.create(name='book2', price=100)

        url = reverse('books-list')
        response = self.client.get(url)
        serializer_data = BookSerializer((book_1, book_2), many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
