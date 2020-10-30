from django.forms import ModelForm, Textarea
from auctions.models import Auction_listing


class  Auction_listing_form(ModelForm):
    class Meta:
        model = Auction_listing
        fields = ['commodity_title', 'description', 'starting_price', 'URL_image', 'category']
        widgets = {
            'description': Textarea(attrs={'cols': 40, 'rows': 6})
        }