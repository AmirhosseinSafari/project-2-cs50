# Generated by Django 3.0.6 on 2020-10-28 15:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auction_listing_bids_categories_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_listing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients_sellings', to='auctions.Auction_listing')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
