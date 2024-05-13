# myapp/urls.py

from django.urls import path, include
from .views import views

urlpatterns = [

    # customers
    path('create-customer/', views.create_customer, name='create_customer'),
    # path('customer/<str:identifier>/', views.get_customer, name='get_customer'),
    path('customer/', views.get_customer, name='get_customer'),
    # path('phone-customer/<str:identifier>', views.get_customer, name='phone_customer'),
    
    # listings
    path('newlisting', views.new_listing, name='newlisting'),
    path('mylistings/<str:identifier>/', views.get_mylistings, name='get_mylistings'),
    path('updatelisting', views.updatelisting, name='newlisting'),

    # transactions
    path('payments/<str:identifier>/', views.get_mypayments, name='get_mypayments'),
    path('receivals/<str:identifier>/', views.get_myreceivals, name='get_myreceivals'),
    path('listing/<int:listing_id>/transactions/', views.listing_transactions, name='get_transactions'),

]

