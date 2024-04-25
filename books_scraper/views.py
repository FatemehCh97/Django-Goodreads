from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from .utils import get_book_info, search_quotes_scrapy
from .models import Book, Quote
from django.db.models import Q
from bs4 import BeautifulSoup
import requests


def home(request):
    return render(request, 'books_scraper/home.html')


def search(request):
    if request.method == 'GET':
        search_query = request.GET.get('search_query', '')
        search_type = request.GET.get('search_type', '')

        if search_query:
            if search_type == 'quotes':
                return redirect('search_result_quotes',
                                search_query=search_query)
            elif search_type == 'books':
                return redirect('search_results',
                                search_query=search_query)

    return render(request, 'books_scraper/search_form.html')


def search_results(request, search_query):
    book_info_list = []  # Initialize Book Information list

    # Scraping books from Goodreads for pages 1 to 10
    for page in range(1, 11):
        url = (f'https://www.goodreads.com/'
               f'search?q={search_query}&page={page}')
        headers = {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/50.0.2661.102 Safari/537.36')
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                bsobj = BeautifulSoup(response.content, 'html.parser')
                book_items = bsobj.find("table",
                                        class_="tableList").find_all('tr')

                for book in book_items:
                    book_url = ("https://www.goodreads.com" +
                                book.find('a')['href'])

                    # Get book information using get_book_info function
                    (title, author, avg_rating,
                     rating_count, review_count, genres,
                     num_pages, publish_date, goodreads_id, book_url) = \
                        get_book_info(book_url, headers)

                    # Append book information to the list
                    book_info_list.append({
                        'title': title,
                        'author': author,
                        'avg_rating': avg_rating,
                        'rating_count': rating_count,
                        'review_count': review_count,
                        'genres': genres,
                        'num_pages': num_pages,
                        'publish_date': publish_date,
                        'search_query': search_query,
                        'goodreads_id': goodreads_id,
                        'goodreads_url': book_url
                    })
            # Extract genres from book_info_list
            genres = set()  # Initialize genres set
            for book_info in book_info_list:
                genres.update(book_info['genres'])
        except Exception as e:
            print(f"Error scraping book information: {e}")

    # Render the search results template with the book information list
    return render(request, 'books_scraper/search_results.html',
                  {'book_info_list': book_info_list,
                   'search_query': search_query,
                   'genres': sorted(genres)})


def filter_results(request, search_query):
    # Extract filter parameters from the request
    genre = request.GET.get('genres')
    min_rating = request.GET.get('min_rating')
    max_rating = request.GET.get('max_rating')
    publish_date_start = request.GET.get('publish_date_start')
    publish_date_end = request.GET.get('publish_date_end')

    # Construct Q objects for filtering
    filters = (Q(title__icontains=search_query) |
               Q(author__icontains=search_query))
    if genre:
        filters &= Q(genres__icontains=genre)
    if min_rating:
        filters &= Q(average_rating__gte=min_rating)
    if max_rating:
        filters &= Q(average_rating__lte=max_rating)
    if publish_date_start and not publish_date_end:
        filters &= Q(publish_date__gte=publish_date_start)
    elif not publish_date_start and publish_date_end:
        filters &= Q(publish_date__lte=publish_date_end)
    elif publish_date_start and publish_date_end:
        filters &= Q(publish_date__range=(publish_date_start,
                                          publish_date_end))

    # Apply filters to retrieve matching books
    book_info_list = Book.objects.filter(filters)

    return render(request, 'books_scraper/filter_results.html',
                  {'book_info_list': book_info_list,
                   'search_query': search_query,
                   'result_count': book_info_list.count()})


def book_detail(request, goodreads_id):
    try:
        book = Book.objects.get(goodreads_id=goodreads_id)
        book_info = {
            'title': book.title,
            'author': book.author,
            'avg_rating': book.average_rating,
            'rating_count': book.rating_count,
            'review_count': book.review_count,
            'genres': book.genres,
            'num_pages': book.num_pages,
            'publish_date': book.publish_date,
            'goodreads_id': book.goodreads_id,
            'goodreads_url': book.goodreads_url,
        }
        # Get the search_query from the request GET parameters
        search_query = request.GET.get('search_query', '')
        return render(request, 'books_scraper/book_detail.html',
                      {'book_info': book_info, 'search_query': search_query})
    except Book.DoesNotExist:
        return HttpResponseNotFound('<h1>Book not found</h1>')


def search_result_quotes(request, search_query):
    quotes_info_list = []

    for page in range(1, 6):
        url = (f"https://www.goodreads.com/search?q={search_query}"
               f"&search_type=quotes&tab=quotes&page={page}")
        headers = {
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/50.0.2661.102 Safari/537.36')
        }
        try:
            # Call the function to scrape quotes from Goodreads
            quotes_info_list += search_quotes_scrapy(url, headers)

            # Save the scraped quotes to the database
            for quote_info in quotes_info_list:
                quote = Quote.objects.create(
                    quote=quote_info['quote'],
                    author=quote_info['author'],
                    likes=quote_info['likes']
                )
                quote.save()

        except Exception as e:
            print(f"Error scraping quotes for search query: {e}")

    # Render the search results template with the quotes information list
    return render(request, 'books_scraper/search_results_quotes.html',
                  {'quotes_info_list': quotes_info_list})
