from django.db import models


# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    average_rating = models.FloatField()
    rating_count = models.IntegerField()
    review_count = models.IntegerField()
    genres = models.TextField(null=True)
    num_pages = models.IntegerField(null=True)
    publish_date = models.DateField(null=True)
    goodreads_id = models.CharField(max_length=20, unique=True)
    goodreads_url = models.URLField()

    def __str__(self):
        return self.title


class BookHTML(models.Model):
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    html_content = models.TextField()
    goodreads_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"BookHTML - {self.goodreads_id}"


class Quote(models.Model):
    quote = models.TextField()
    author = models.CharField(null=True, max_length=100)
    likes = models.IntegerField(null=True)

    def __str__(self):
        return self.quote
