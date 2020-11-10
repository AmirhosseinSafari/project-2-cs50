from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    #auction_list = models.ManyToManyField(Auction_listing, blank=True, related_name="user_lists") 
    def __str__(self):
        return f"id: {self.id}, username: {self.username}, email: {self.email}"

class Comments(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=2000)
    created_time = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"author: {self.author.username}, text: {self.text}"
    
class Categories(models.Model):
    category = models.CharField(max_length=50)

    def __str__(self):
        return f"category: {self.category}"

class Bids(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"bidder: {self.bidder.username}, amount: {self.amount}"


class Auction_listing(models.Model): #card
    commodity_title = models.CharField(max_length=100, help_text="This title going to be shown in head of your listing")
    created_time = models.DateField(auto_now_add=True)
    bids = models.ManyToManyField(Bids)
    comments = models.ManyToManyField(Comments)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=2000, help_text="Give more information about your comodity to sell it faster!")
    starting_price = models.DecimalField(max_digits=9, decimal_places=2, help_text="Enter base price of your commodity")
    URL_image = models.CharField(max_length=2000, blank=True, help_text="Url of image that going to be displayed on your listing")
    category = models.CharField(max_length=50, help_text="write category type of your listing")
    #note: first should update categoties then this category
    def __str__(self):
        return f"commodity: {self.commodity_title}, created time: {self.created_time}"


class User_listing(models.Model):
    user = models.ForeignKey( User, on_delete=models.CASCADE, related_name="clients")
    listing = models.ForeignKey( Auction_listing,  on_delete=models.CASCADE, related_name="clients_sellings")

    def __str__(self):
        return f"user: {self.user.username}, listing: {self.listing.commodity_title}, listing_id: {self.listing.id}"