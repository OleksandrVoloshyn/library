import json

from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Avg, Case, Count, When
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APITestCase

from apps.store.models import BookModel, UserBookRelationModel
from apps.store.serializers import BookSerializer


class BooksApiTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='test_name')
        self.book_1 = BookModel.objects.create(name='book1', price=1000, author_name='Author1', owner=self.user)
        self.book_2 = BookModel.objects.create(name='book2', price=100, author_name='Author2')
        self.book_3 = BookModel.objects.create(name='book3 Author1', price=100, author_name='Author3')

        UserBookRelationModel.objects.create(user=self.user, book=self.book_1, like=True, rate=4)

    def test_get(self):
        url = reverse('books-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))

        books = BookModel.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelationmodel__like=True, then=1)))).order_by('id')
        serializer_data = BookSerializer(books, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
        self.assertEqual(serializer_data[0]['rating'], '4.00')
        self.assertEqual(serializer_data[0]['annotated_likes'], 1)

    def test_retrieve(self):
        url = reverse('books-detail', args=(self.book_1.id,))
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual('book1', response.data['name'])

    def test_get_filter(self):
        url = reverse('books-list')
        response = self.client.get(url, data={'price': 100})
        books = BookModel.objects.filter(id__in=(self.book_2.id, self.book_3.id)).annotate(
            annotated_likes=Count(Case(When(userbookrelationmodel__like=True, then=1))))
        serializer_data = BookSerializer(books, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    #
    def test_get_search(self):
        url = reverse('books-list')
        response = self.client.get(url, data={'search': 'Author1'})
        BookModel.objects.filter()
        books = BookModel.objects.filter(id__in=[self.book_1.id, self.book_3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelationmodel__like=True, then=1))))
        serializer_data = BookSerializer(books, many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('books-list')
        response = self.client.get(url, data={'ordering': 'price'})
        books = BookModel.objects.filter(id__in=(self.book_2.id, self.book_3.id, self.book_1.id)).annotate(
            annotated_likes=Count(Case(When(userbookrelationmodel__like=True, then=1)))).order_by('price')
        serializer_data = BookSerializer(books, many=True).data

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


class BookRelationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(username='user_name')
        self.user2 = User.objects.create(username='user2_name')
        self.book_1 = BookModel.objects.create(name='book1', price=1000, author_name='Author1', owner=self.user)
        self.book_2 = BookModel.objects.create(name='book2', price=100, author_name='Author2')

    def test_like(self):
        url = reverse('book_relations-detail', args=(self.book_1.id,))
        data = {'like': True, }
        json_data = json.dumps(data)

        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelationModel.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.like)

    def test_in_bookmarks(self):
        url = reverse('book_relations-detail', args=(self.book_1.id,))
        self.client.force_login(self.user)

        data = {'in_bookmarks': True, }
        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelationModel.objects.get(user=self.user, book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse('book_relations-detail', args=(self.book_1.id,))
        data = {'rate': 3, }
        self.client.force_login(self.user)

        json_data = json.dumps(data)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelationModel.objects.get(user=self.user, book=self.book_1)
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse('book_relations-detail', args=(self.book_1.id,))
        data = {'rate': 6, }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual({'rate': [ErrorDetail(string='"6" is not a valid choice.', code='invalid_choice')]},
                         response.data)
