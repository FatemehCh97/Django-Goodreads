from django.contrib import admin
from django.contrib.admin import register
from .models import Book, BookHTML, Quote


# Register your models here.
@register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'goodreads_id', 'publish_date')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'author', 'goodreads_id')


@register(BookHTML)
class BookHTMLAdmin(admin.ModelAdmin):
    list_display = ('id', 'goodreads_id', 'html_content')
    list_display_links = ('id', 'goodreads_id')


@register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'quote', 'author', 'likes')
    search_fields = ('author', )
