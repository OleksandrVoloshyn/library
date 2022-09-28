import json

from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from apps.store.models import BookModel
from apps.store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_name')
        self.book_1 = BookModel.objects.create(name='book1', price=1000, author_name='Author1', owner=self.user)
        self.book_2 = BookModel.objects.create(name='book2', price=100, author_name='Author2')
        self.book_3 = BookModel.objects.create(name='book3 Author1', price=100, author_name='Author3')

    def test_get(self):
        url = reverse('books-list')
        response = self.client.get(url)
        serializer_data = BookSerializer((self.book_1, self.book_2, self.book_3), many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_retrieve(self):
        url = reverse('books-detail', args=(self.book_1.id,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('book1', response.data['name'])

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

    def test_create(self):
        self.assertEqual(3, BookModel.objects.count())
        url = reverse('books-list')
        data = {
            'name': 'test',
            'price': '20.00',
            'author_name': 'author'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, json_data, content_type='application/json')

        self.assertEqual(4, BookModel.objects.count())
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.user, BookModel.objects.last().owner)

    def test_update(self):
        url = reverse('books-detail', args=(self.book_1.id,))
        data = {
            'name': self.book_1.name,
            'price': self.book_1.price,
            'author_name': 'Author'
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, json_data, content_type='application/json')

        self.book_1.refresh_from_db()
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('Author', self.book_1.author_name)

    def test_delete(self):
        self.assertEqual(3, BookModel.objects.count())
        url = reverse('books-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)
        response = self.client.delete(url)

        self.assertEqual(2, BookModel.objects.count())
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_not_owner(self):
        self.user2 = User.objects.create(username='test_name2')
        self.client.force_login(self.user2)

        self.assertEqual(3, BookModel.objects.count())
        url = reverse('books-detail', args=(self.book_1.id,))
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, BookModel.objects.count())
        self.assertEqual({'detail': ErrorDetail(string='You do not have permission to perform this action.',
                                                code='permission_denied')}, response.data)

    def test_delete_not_owner_but_staff(self):
        self.assertEqual(3, BookModel.objects.count())
        self.user3 = User.objects.create(username='test_name3', is_staff=True)
        url = reverse('books-detail', args=(self.book_1.id,))
        self.client.force_login(self.user3)
        response = self.client.delete(url)

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, BookModel.objects.count())
