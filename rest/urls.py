from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import views, viewslistings, viewstransactions, viewscustomers, viewsbids


urlpatterns = [

    #new customers
    path('upload-id/', viewscustomers.upload_id, name='upload_id'), #not working
    path('upload-topup/', viewscustomers.upload_topup, name='upload_id'), #not working
    path('email-customer/<str:id>/', viewscustomers.get_customer_email, name='email_customer'),
    path('customer/update/<int:id>/', viewscustomers.update_customer, name='update_customer'), 
    path('my-kpis/<str:email>/', viewscustomers.customer_info, name='my_kpis'), 

    # new listings
    path('listings/', viewslistings.all_listings, name='listings'),
    path('listing/<str:slug>', viewslistings.listing_detail, name='listing_detail'),
    path('my-listings/<str:identifier>', viewslistings.my_listings, name='get_mylistings'),
    path('create-listing', viewslistings.create_listing, name='create_listing'),
    path('listing-images/<str:slug>', viewslistings.listing_images, name='listing_images'),

    # new offers
    path('bid', viewsbids.post_bid, name='bid'),
    path('bids/<str:slug>', viewsbids.get_bids, name='bid'),
    path('my-bids/<str:email>', viewsbids.get_my_bids, name='bid'),
    

]

