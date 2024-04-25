from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search', views.search,
         name='search'),
    path('search_results/<str:search_query>/',
         views.search_results, name='search_results'),
    path('book/<str:goodreads_id>/', views.book_detail,
         name='book_detail'),
    path('search_result_quotes/<str:search_query>/',
         views.search_result_quotes, name='search_result_quotes'),
    path('filter_results/<str:search_query>/',
         views.filter_results, name='filter_results'),
]
