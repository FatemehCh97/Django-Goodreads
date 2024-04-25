# Goodreads Book Scraper

This project is a Django-based web application that allows users to search for books and quotes on Goodreads and view detailed information about them.

## Features

- Search for books by title or author.
- View search results with book details.
- Filter book search results by genres, rating and published date
- View detailed information about a specific book.
- Search for quotes by keywords
- View a list of quotes with their authors and likes
- Automatically save search data to the database for future reference (avoiding duplication).
- Admin interface for managing datas.

## Installation

1. Open a terminal or command prompt and navigate to the project directory.

    ```bash
    cd blog_project
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Apply database migrations:

    ```bash
   python manage.py makemigrations
    python manage.py migrate
    ```

4. Create a superuser for accessing the admin interface:

    ```bash
    python manage.py createsuperuser
    ```

5. Start the development server:

    ```bash
    python manage.py runserver
    ```

6. Open your web browser and navigate to `http://127.0.0.1:8000/` to access the application.

## Usage

- Go to the main page (http://localhost:8000/search) to search for books or quotes.
- EEnter a search query (book title or author) and click "Search Books" to search for books.
- Enter a search query (quote keyword) and click "Search Quotes" to search for quotes.
- View the search results and click on a book to see detailed information.
- On the book details page (http://localhost:8000/book/{goodreads_id}/), you can navigate back to the search results or the search page.
- Access the admin interface at `http://127.0.0.1:8000/admin/` to manage datas as a superuser.

**Note:**

The book search results will be displayed at http://localhost:8000/search_results/{search_query}/.
The quote search results will be displayed at http://localhost:8000/search_result_quotes/{search_query}/.