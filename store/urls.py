from django.urls import path
from .views import home, robots_txt
from .views import home, products
urlpatterns = [
    path('', home, name='home'),
    path('robots.txt', robots_txt),
     path('products/', products, name='products'),
]