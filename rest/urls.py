from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import views, viewslistings, viewstransactions, viewscustomers, viewsbids, viewsbackoffice


urlpatterns = [

    #new customers
    path('upload-id/', viewscustomers.upload_id, name='upload_id'), #not working
    path('upload-topup/', viewscustomers.upload_topup, name='upload_id'), #not working
    path('email-customer/<str:id>/', viewscustomers.get_customer_email, name='email_customer'),
    path('customer/<str:id>/', viewscustomers.get_customer_id, name='email_customer'),
    path('customer/update/<int:id>/', viewscustomers.update_customer, name='update_customer'), 
    path('my-kpis/<str:email>/', viewscustomers.customer_info, name='my_kpis'), 

    # new listings
    path('listings/', viewslistings.all_listings, name='listings'),
    path('listing/<str:slug>', viewslistings.listing_detail, name='listing_detail'),
    path('listing-id/<int:id>', viewslistings.listing_id, name='listing_detail'),
    path('my-listings/<str:identifier>', viewslistings.my_listings, name='get_mylistings'),
    path('create-listing', viewslistings.create_listing, name='create_listing'),
    path('listing-images/<str:slug>', viewslistings.listing_images, name='listing_images'),
    path('listing-category/<str:categ>/', viewslistings.listings_category, name='listing_category'),
    path('listing-search/', viewslistings.search_listings, name='listing-search'),

    # new offers
    path('bid', viewsbids.post_bid, name='bid'),
    path('bids/<str:slug>', viewsbids.get_bids, name='bid'),
    path('my-bids/<str:email>', viewsbids.get_my_bids, name='bid'),
    
    

    #transactions
    path('accept-offer', viewstransactions.accept_offer, name='accept-offer'),
    path('create-transaction', viewstransactions.new_payment_order, name='create-transaction'),
    path('transaction/<str:serial_number>', viewstransactions.transaction, name='transaction'),
    path('confirm-transaction', viewstransactions.confirm_transaction, name='confirm-transaction'),
    path('dispute-transaction', viewstransactions.dispute_transaction, name='dispute-transaction'),
    path('my-purchases/<str:email>', viewstransactions.my_purchases, name='my-purchases'),
    path('my-sales/<str:email>', viewstransactions.my_sales, name='my-sales'),


    # backoffice calls
    path('close-auctions', viewsbackoffice.close_auctions , name='create-transaction'),                     # closes auctions
    path('hold_listing', viewsbackoffice.hold_listing , name='hold_listing'),                         # forces seller to accept offer
    path('force-confirm-payment', viewsbackoffice.force_confirm_payment , name='create-transaction'),       # forces buyer to confirm payment
    path('force-confirm-delivery', viewsbackoffice.force_confirm_delivery ,name='create-transaction'),      # forces seller to confirm delivery
    path('force-dispute-statement', viewsbackoffice.force_dispute_statement , name='create-transaction'),   # forces statement from dispute's parties

]

