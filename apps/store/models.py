from django.db import models


class BookModel(models.Model):
    class Meta:
        db_table = 'books'

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
