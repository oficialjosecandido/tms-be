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
    path('listings/', views.listings, name='listings'),
    path('newlisting', views.new_listing, name='newlisting'),
    path('mylistings/<str:identifier>/', views.get_mylistings, name='get_mylistings'),
    path('updatelisting', views.updatelisting, name='newlisting'),
    path('upload-images/', views.upload_images, name='upload_images'),

    # transactions
    path('charge/', views.stripe_charge, name='charge'),
    path('new_payment', views.new_payment, name='new_payment'),
    path('payments/<str:identifier>/', views.get_mypayments, name='get_mypayments'),
    path('receivals/<str:identifier>/', views.get_myreceivals, name='get_myreceivals'),
    path('listing/<int:listing_id>/transactions/', views.listing_transactions, name='get_transactions'),

]

