# myapp/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import views, viewslistings, viewstransactions, viewscustomers

# Create a router for the CommentViewSet
""" router = DefaultRouter()
router.register(r'comments', viewslistings.CommentViewSet) """

urlpatterns = [

    # customers
    path('create-customer/', views.create_customer, name='create_customer'),
    path('get-customer/<int:id>/', viewscustomers.get_create_customer, name='get_customer'),
    path('email-customer/<str:id>/', viewscustomers.get_customer_email, name='email_customer'),
    path('customer/<int:id>/', viewscustomers.customer_detail, name='customer_detail'),
    path('request-withdraw/', viewscustomers.request_withdraw, name='request-withdraw'),
    
    # listings
    path('listings/', views.listings, name='listings'),
    path('newlisting', viewslistings.create_listing, name='newlisting'),
    path('mylistings/<str:identifier>/', viewslistings.my_listings, name='get_mylistings'),
    path('update-listing/<int:id>/', viewslistings.update_listing_status, name='newlisting'),
    path('upload-images/', views.upload_images, name='upload_images'),
    path('listings/<int:id>/', viewslistings.listing_detail, name='listing_detail'),
    path('create-comment/', viewslistings.create_comment, name='create-comment'),
    path('comments/<int:id>', viewslistings.get_comments, name='comments'),

    # transactions
    path('charge/', views.stripe_charge, name='charge'),
    path('new_payment', views.new_payment, name='new_payment'),
    path('payments/<str:identifier>/', views.get_mypayments, name='get_mypayments'),
    path('receivals/<str:identifier>/', views.get_myreceivals, name='get_myreceivals'),
    path('listing/<int:listing_id>/transactions/', views.listing_transactions, name='get_transactions'),

]

