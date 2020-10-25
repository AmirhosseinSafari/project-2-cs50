from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class auction():
    pass


#You will also need to add additional models to this 
# file to represent details about auction 
# listings, bids, comments, and auction categories.