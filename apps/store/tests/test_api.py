from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.store.models import BookModel
from apps.store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.book_1 = BookModel.objects.create(name='book1', price=1000, author_name='Author1')
        self.book_2 = BookModel.objects.create(name='book2', price=100, author_name='Author2')
        self.book_3 = BookModel.objects.create(name='book3 Author1', price=100, author_name='Author3')

    def test_get(self):
        url = reverse('books-list')
        response = self.client.get(url)
        serializer_data = BookSerializer((self.book_1, self.book_2, self.book_3), many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_filter(self):
        url = reverse('books-list')
        response = self.client.get(url, data={'price': 100})
        serializer_data = BookSerializer((self.book_2, self.book_3), many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('books-list')
        response = self.client.get(url, data={'search': 'Author1'})
        serializer_data = BookSerializer((self.book_1, self.book_3), many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('books-list')
        response = self.client.get(url, data={'ordering': 'price'})
        serializer_data = BookSerializer((self.book_2, self.book_3, self.book_1), many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
