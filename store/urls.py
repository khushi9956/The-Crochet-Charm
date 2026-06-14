from django.urls import path
from .views import home, robots_txt

urlpatterns = [
    path('', home, name='home'),
    path('robots.txt', robots_txt),
]