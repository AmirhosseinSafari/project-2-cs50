from django.forms import ModelForm, Textarea
from auctions.models import Auction_listing, Bids
from django import forms

class  Auction_listing_form(ModelForm):
    commodity_title = forms.CharField( 
        required=True, 
        widget= forms.TextInput(
        attrs={"placeholder": "title of listing"}
        )
        )

    description = forms.CharField(
        required=True,
        widget=forms.Textarea(
        attrs={"cols": 10, "rows": 6, "class": "form_description"}
        )
        )

    class Meta:
        model = Auction_listing
        fields = ['commodity_title', 'description', 'starting_price', 'URL_image', 'category']
        widgets = {
            'description': Textarea(attrs={'cols': 40, 'rows': 6})
        }


class Bids_form(ModelForm):
    amount = forms.DecimalField(required=True,
    widget=forms.NumberInput(
        attrs={"name": "user_bid", "placeholder": "Your bid"}
    )
    )

    class Meta:
        model = Bids
        fields = ['amount']
