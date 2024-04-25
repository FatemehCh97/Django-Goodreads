from django.db import IntegrityError
from .models import Book, BookHTML
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import re


def get_book_info(book_url, headers):
    try:
        response = requests.get(book_url, headers=headers)

        if response.status_code == 200:
            bsobj = BeautifulSoup(response.content, 'html.parser')

            goodreads_id = re.search(r'(?<=show/)\d+', book_url).group()

            title = bsobj.find("h1",
                               class_="Text__title1").text.strip()

            # Extract author
            author = bsobj.find("span",
                                class_="ContributorLink__name").text

            # Extract average rating
            average_rating = bsobj.find("div",
                                        class_="RatingStatistics__rating"
                                        ).text

            # Extract rating count
            rating_count_text = (bsobj.find("span",
                                            {"data-testid": "ratingsCount"})
                                 .text.strip())
            # Extract only digits from the text
            rating_count = int(''.join(filter(lambda x: x.isdigit(),
                                              rating_count_text)))

            # Extract review count
            review_count_text = bsobj.find("span",
                                           class_="u-dot-before").text
            # Extract only digits from the text
            review_count = int(''.join(filter(lambda x: x.isdigit(),
                                              review_count_text)))

            # Extract genres
            genre_buttons = bsobj.find("div",
                                       class_="BookPageMetadataSection"
                                              "__genres")
            if genre_buttons:
                genre_list = genre_buttons.find_all("a",
                                                    class_="Button Button--"
                                                           "tag-inline Button"
                                                           "--small")
                genres = [button.span.text for button in genre_list]
            else:
                genres = None

            # Extract number of pages
            pages_info = bsobj.find("p", {"data-testid": "pagesFormat"})

            if pages_info:
                num_pages_str = pages_info.text.strip().split()[0]
                try:
                    num_pages = int(num_pages_str)
                except ValueError:
                    # Handle cases where num_pages_str is not a valid integer
                    num_pages = None
            else:
                num_pages = None

            # Extract publication date
            publication_info = bsobj.find("p",
                                          {"data-testid": "publicationInfo"})

            if publication_info:
                publication_date = publication_info.text.strip()

                if "First published" in publication_date:
                    publish_date = publication_date.split("First published"
                                                          )[-1].strip()
                elif "Expected publication" in publication_date:
                    publish_date = publication_date.split(
                        "Expected publication")[-1].strip()
                else:
                    publish_date = publication_date.split("Published"
                                                          )[-1].strip()

                # Convert publish_date to YYYY-MM-DD format
                if publish_date:
                    publish_date = datetime.strptime(publish_date,
                                                     '%B %d, %Y'
                                                     ).strftime('%Y-%m-%d')
            else:
                publish_date = None

            # Check if a html with the same goodreads_id already exists
            existing_book_html = BookHTML.objects.filter(
                goodreads_id=goodreads_id).first()
            if existing_book_html:
                print(f"HTML content for book with goodreads_id"
                      f" {goodreads_id} already exists. Skipping.")

            # Check if a book with the same goodreads_id already exists
            existing_book = Book.objects.filter(goodreads_id=goodreads_id
                                                ).first()

            if existing_book:
                # Update existing book with new information
                # Retrieve static information from the database
                existing_book.average_rating = average_rating
                existing_book.rating_count = rating_count
                existing_book.review_count = review_count
                existing_book.genres = genres
                existing_book.save()
                print(f"Updated book with goodreads_id {goodreads_id}")
            else:
                # Insert the new book into the database
                try:
                    new_book = Book.objects.create(
                        title=title,
                        author=author,
                        average_rating=average_rating,
                        rating_count=rating_count,
                        review_count=review_count,
                        genres=genres,
                        num_pages=num_pages,
                        publish_date=publish_date,
                        goodreads_id=goodreads_id,
                        goodreads_url=book_url,
                    )
                    print(f"Inserted book with goodreads_id {goodreads_id}")

                    # Insert BookHTML content for new book
                    html_content = str(bsobj)
                    try:
                        new_book_html = BookHTML.objects.create(
                            book=new_book,
                            html_content=html_content,
                            goodreads_id=goodreads_id
                        )
                        print(f"Inserted HTML content for book"
                              f" with goodreads_id {goodreads_id}")
                    except IntegrityError as e:
                        print(
                            f"Error inserting HTML content for"
                            f" goodreads_id {goodreads_id}: {e}")

                except IntegrityError as e:
                    print(f"Error inserting book with "
                          f"goodreads_id {goodreads_id}: {e}")

            return (title, author, average_rating,
                    rating_count, review_count, genres,
                    num_pages, publish_date, goodreads_id, book_url)
        else:
            print(f"Failed to fetch book information from {book_url}."
                  f" Status code: {response.status_code}")
            return None, None, None, None, None, None, None, None, None, None
    except Exception as e:
        print(f"Error extracting book information from {book_url}: {e}")
        return None, None, None, None, None, None, None, None, None, None


def search_quotes_scrapy(quote_url, headers):
    try:
        response = requests.get(quote_url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            quotes_table = soup.find("table", class_="tableList")
            if quotes_table:
                quotes_info_list = []
                rows = quotes_table.find_all("tr")
                for row in rows:
                    quote_div = row.find("div", class_="quoteText")
                    if quote_div:
                        quote_text = quote_div.text.strip().split('\n')[0]
                        author_info = row.find("a", class_="authorOrTitle")
                        if author_info:
                            author = author_info.text.strip()
                        else:
                            author = None
                        likes_info = row.find("a", class_="actionLinkLite")
                        if likes_info:
                            likes = likes_info.text.strip().split()[0]
                        else:
                            likes = None
                        quotes_info_list.append({
                            'quote': quote_text,
                            'author': author,
                            'likes': likes
                        })
                print("Find ", len(quotes_info_list), " quotes in this page")
                return quotes_info_list
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error scraping quotes: {e}")
        return None
