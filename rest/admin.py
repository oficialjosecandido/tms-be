from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Customer)
admin.site.register(Listing)
admin.site.register(Transaction)
admin.site.register(Bid)
admin.site.register(ListingImage)