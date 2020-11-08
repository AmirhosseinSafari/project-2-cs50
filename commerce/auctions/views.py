from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Auction_listing, Bids

from .models import User
from .forms import Auction_listing_form, Bids_form

def index(request):
    context = {
        "auctions_listing": Auction_listing.objects.all()
    }
    return render(request, "auctions/index.html", context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def new_listing(request):

    if request.method == "POST":
        form = Auction_listing_form(request.POST)
        try:
            if form.valid():
                new = form.save(commit=False)
                assert request.user.is_authenticated
                new.creator = request.user
                new.save()
                messages.success(request, "Your listing is saved successfully")
                return HttpResponseRedirect(reverse(index))

        except ValueError:
            return render(request, "auctions/messages.html", {
                "message": "Error! in saving auction proccess..."
            })
        
    else:
        form = Auction_listing_form()
        return render(request, "auctions/new_listing.html", {
            "form": form
        })

@login_required
def listing (request, listing_id):

    if request.method == "POST":

        bid_form = Bids_form(request.POST or None)
        new_bid = bid_form['amount'].value()
        new_bid = float (new_bid)

        old_bid = Auction_listing.objects.get(id=listing_id).bids.first()
        print(old_bid)

        if old_bid == None:
            old_bid = 0
        else:
            old_bid = old_bid.amount

        starting_price = str (Auction_listing.objects.get(id=listing_id).starting_price )

        if ( new_bid < old_bid ) or ( new_bid < float (starting_price) ):
            content = {
            "listing": Auction_listing.objects.get(id=listing_id),
            "error_message": "Error: You can NOT bid less than the price!",
            "bid_form": bid_form
            }
            return render(request, "auctions/listing.html", content)
        else:

            
            user_bid = Bids(bidder=request.user, amount=new_bid)
            bid_form = Bids_form(request.POST, instance=user_bid)
            
            listing = Auction_listing.objects.get(id=listing_id)
            

            if bid_form.is_valid():
                bid_form.save()
                messages.success(request, "Thanks, your bid was created successfully!")
            
            listing.bids.add(user_bid)
            #todo: passing comments
            
            return HttpResponseRedirect( reverse( "listing", args=(listing_id,) ) )
    
    else:
        bid_form = Bids_form(request.POST or None)
        
        content = {
            "listing": Auction_listing.objects.get(id=listing_id),
            "bid_form": bid_form
        }

        return render(request, "auctions/listing.html", content)

