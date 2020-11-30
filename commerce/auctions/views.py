from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Auction_listing, Bids, Comments, Categories

from .models import User, User_listing
from .forms import Auction_listing_form, Bids_form, Comments_form

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
            new = form.save(commit=False)
            assert request.user.is_authenticated
            new.creator = request.user
            new.save()
            messages.success(request, "Your listing is saved successfully")
            
            category = request.POST
            new_category = Categories.create(category['category']) 
            new_category.save()

            return HttpResponseRedirect(reverse(index))

        except ValueError as error:
            print(error)
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
        comments_form = Comments_form(request.POST or None)

        new_bid = bid_form['amount'].value()
        new_comment = comments_form['text'].value()

        #-----------------------------------------------------------------------
        # Closing
        #-----------------------------------------------------------------------
        
        if "close_listing" in request.POST and (request.user == Auction_listing.objects.get(id=listing_id).creator):
            Auction_listing.objects.filter(id=listing_id).update(closed=True)

        if not (Auction_listing.objects.get(id=listing_id).closed) :
        
            #-----------------------------------------------------------------------
            # Creating bids
            #-----------------------------------------------------------------------

            if new_bid != None:

                new_bid = float (new_bid)
                old_bid = Auction_listing.objects.get(id=listing_id).bids.first()
                #print(old_bid)

                if old_bid == None:
                    old_bid = 0
                else:
                    old_bid = old_bid.amount

                starting_price = str (Auction_listing.objects.get(id=listing_id).starting_price )

                #-----------------------------------------------------------------------
                # Checking that bid isn't lower than price
                #-----------------------------------------------------------------------

                if ( new_bid < old_bid ) or ( new_bid <= float (starting_price) ):
                    all_comments = Auction_listing.objects.get(id=listing_id).comments.all()
                    all_comments_list = []

                    for comment in all_comments:
                        all_comments_list.append(comment)

                    watchlist = User_listing.objects.filter( user=request.user, listing=Auction_listing.objects.get(id=listing_id) )

                    content = {
                    "listing": Auction_listing.objects.get(id=listing_id),
                    "error_message": "Error: You can NOT bid less than or equal to the price!",
                    "bid_form": bid_form,
                    "comments_form": comments_form,
                    "comments": all_comments_list,
                    "watchlist": watchlist
                    }
                    return render(request, "auctions/listing.html", content)
                else:
                    #-----------------------------------------------------------------------
                    # Commiting bid
                    #-----------------------------------------------------------------------

                    user_bid = Bids(bidder=request.user, amount=new_bid)
                    bid_form = Bids_form(request.POST, instance=user_bid)

                    listing = Auction_listing.objects.get(id=listing_id)

                    if bid_form.is_valid():
                        bid_form.save()
                        messages.success(request, "Thanks, your bid was created successfully!")
                        Auction_listing.objects.filter(id=listing_id).update(starting_price=new_bid)
                        listing.bids.add(user_bid)

        #-----------------------------------------------------------------------
        # If listing closed
        #-----------------------------------------------------------------------

        else:

            all_comments = Auction_listing.objects.get(id=listing_id).comments.all()
            all_comments_list = []

            for comment in all_comments:
                all_comments_list.append(comment)

            watchlist = User_listing.objects.filter( user=request.user, listing=Auction_listing.objects.get(id=listing_id) )

            content = {
            "listing": Auction_listing.objects.get(id=listing_id),
            "bid_form": "",
            "comments_form": comments_form,
            "comments": all_comments_list,
            "watchlist": watchlist
            }

            return render(request, "auctions/listing.html", content)

        #-----------------------------------------------------------------------
        # Creating commetns
        #-----------------------------------------------------------------------

        if new_comment != None:
            
            user_comment = Comments(author=request.user, text=new_comment)
            comment_form = Comments_form(request.POST, instance=user_comment)

            listing = Auction_listing.objects.get(id=listing_id)

            if comment_form.is_valid():
                comment_form.save()
                messages.success(request, "Thanks, your comment was created successfully!")
                listing.comments.add(user_comment)
        
        
        #-----------------------------------------------------------------------
        # Creating watchlist
        #-----------------------------------------------------------------------

        if "add_to_watchlist" in request.POST:
            watchlist_listing = User_listing(user=request.user, listing=Auction_listing.objects.get(id=listing_id) )
            watchlist_listing.save()
            messages.success(request, "Listing added to your watchlist successfully!")
            
        if "remove_from_watchlist" in request.POST:
            watchlist_listing = User_listing.objects.get( user=request.user, listing=Auction_listing.objects.get(id=listing_id) )
            watchlist_listing.delete()

        return HttpResponseRedirect( reverse( "listing", args=(listing_id,) ) )
    
    
    #-----------------------------------------------------------------------
    # Get request
    #-----------------------------------------------------------------------
    
    else:
        
        bid_form = Bids_form(request.POST or None)

        if Auction_listing.objects.get(id=listing_id).closed :
            bid_form = ""

        comments_form = Comments_form(request.POST or None)

        all_comments = Auction_listing.objects.get(id=listing_id).comments.all()
        all_comments_list = []

        for comment in all_comments:
            all_comments_list.append(comment)

        watchlist = User_listing.objects.filter( user=request.user, listing=Auction_listing.objects.get(id=listing_id) )
        
        content = {
            "listing": Auction_listing.objects.get(id=listing_id),
            "bid_form": bid_form,
            "comments_form": comments_form,
            "comments": all_comments_list,
            "watchlist": watchlist
        }

        return render(request, "auctions/listing.html", content)

@login_required
def watchlist(request):

        if request.user.is_authenticated:
            user = request.user
            watchlist = User_listing.objects.filter(user=user)

            #-----------------------------------------------------------------------
            # User listing:
            #       user
            #       listing
            #-----------------------------------------------------------------------
            
            watchlist_arr = []
            for field in watchlist:
                watchlist_arr.append( field.listing )

            content = {
                "watchlist_listing": watchlist_arr
            }
            return render(request, "auctions/watchlist.html", content)


def categories(request):
        
    category = Categories.objects.all()
    content = {
        "categories": category
    }
    return render(request, "auctions/categories.html", content)



def categories_listing(request, category_title):
    
    auctions = Auction_listing.objects.filter(category=category_title)

    content = {
        "auctions": auctions,
        "category_title": category_title
    }

    return render(request, "auctions/category_listing.html", content)





