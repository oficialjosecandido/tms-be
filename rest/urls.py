# myapp/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import views, viewslistings, viewstransactions, viewscustomers, viewsbids

# Create a router for the CommentViewSet
""" router = DefaultRouter()
router.register(r'comments', viewslistings.CommentViewSet) """

urlpatterns = [

    # customers
    path('create-customer/', views.create_customer, name='create_customer'),
    path('get-customer/<int:id>/', viewscustomers.get_create_customer, name='get_customer'), 
    path('customer/<int:id>/', viewscustomers.customer_detail, name='customer_detail'),
    path('request-withdraw/', viewscustomers.request_withdraw, name='request-withdraw'),

    #new customers
    path('upload-id/', viewscustomers.upload_id, name='upload_id'),
    path('upload-topup/', viewscustomers.upload_topup, name='upload_id'),
    path('email-customer/<str:id>/', viewscustomers.get_customer_email, name='email_customer'),
    path('customer/update/<int:id>/', viewscustomers.update_customer, name='update_customer'), 
    path('my-kpis/<str:email>/', viewscustomers.customer_info, name='my_kpis'), 

    # new listings
    path('listings/', viewslistings.all_listings, name='listings'),
    path('listing/<str:slug>', viewslistings.listing_detail, name='listing_detail'),
    path('listing-id/<str:id>', viewslistings.listing_id_detail, name='listing_detail'),
    path('my-listings/<str:identifier>', viewslistings.my_listings, name='get_mylistings'),

    # new offers
    path('bid', viewsbids.post_bid, name='bid'),
    path('bids/<str:slug>', viewsbids.get_bids, name='bid'),
    path('my-bids/<str:email>', viewsbids.get_my_bids, name='bid'),
    
    # listings
    #path('listings/', views.listings, name='listings'),
    path('newlisting', viewslistings.create_listing1, name='newlisting'),
    path('mylistings/<str:identifier>/', viewslistings.my_listings, name='get_mylistings'),
    path('update-listing/<int:id>/', viewslistings.update_listing_status, name='newlisting'),
    path('upload-images/', views.upload_images, name='upload_images'),
    path('listings/<int:id>/', viewslistings.listing_detail, name='listing_detail'),
    path('create-comment/', viewslistings.create_comment, name='create-comment'),
    path('comments/<int:id>', viewslistings.get_comments, name='comments'),

    # transactions
    path('charge/', views.stripe_charge, name='charge'),
    path('new_payment', views.new_payment, name='new_payment'),
    path('payments/<str:identifier>/', viewstransactions.my_payments, name='get_mypayments'),
    path('receivals/<str:identifier>/', views.get_myreceivals, name='get_myreceivals'),
    path('listing/<int:listing_id>/transactions/', views.listing_transactions, name='get_transactions'),

]

