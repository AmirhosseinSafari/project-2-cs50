from django.contrib import admin
from .models import User, Auction_listing, Categories, Bids, User_listing, Comments
# Register your models here.

admin.site.register(User)
admin.site.register(Auction_listing)
admin.site.register(Comments)
admin.site.register(Categories)
admin.site.register(Bids)
admin.site.register(User_listing)
