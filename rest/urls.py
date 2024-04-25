# myapp/urls.py

from django.urls import path, include
from .views import views

urlpatterns = [

    # customers
    path('create-customer/', views.create_customer, name='create_customer'),

    # listings
    path('newlisting', views.new_listing, name='newlisting'),

]

