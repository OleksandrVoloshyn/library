from django.contrib.auth.models import User
from django.db import models


class BookModel(models.Model):
    class Meta:
        db_table = 'books'

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='my_books')
    readers = models.ManyToManyField(User, 'books', through='UserBookRelationModel', )

    def __str__(self):
        return f'{self.id} : {self.name}'


class UserBookRelationModel(models.Model):
    RATE_CHOICES = (
        (1, 'Bad'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Gripping'),
        (5, 'Fascinating')
    )
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)

    user = models.ForeignKey(User, models.CASCADE)
    book = models.ForeignKey(BookModel, models.CASCADE)

    def __str__(self):
        return f'{self.user.username}: {self.book.name}, Rate:{self.rate}'

    def save(self, *args, **kwargs):
        from .services import set_rating

        creating = not self.pk
        old_rating = self.rate
        super().save(*args, **kwargs)
        new_rating = self.rate

        if old_rating is not new_rating or creating:
            set_rating(self.book)
