from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.index, name="home"),
    path('', views.index, name="home"),
    path('menu/', views.menu, name="menu"),
    path('about/', views.about, name="about"),
    path('book/', views.book, name="book"),
    path('contact/', views.contact, name="contact"),
    path('menu_item/<int:pk>/', views.display_menu_item, name="menu_item"),
]