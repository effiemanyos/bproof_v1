"""
PROFILE MODELS FOR USERPROFILE
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """A USER PROFILE MODEL FOR MAINTAINING
    DEFAULT DELIVERY INFORMATION AND ORDER HISTORY
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_phone_number = models.CharField(max_length=20, null=True, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_county = models.CharField(max_length=80, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    CREATE OR UPDATE THE USER PROFILE
    """
    if created:
        UserProfile.objects.create(user=instance)
    # EXISTING USERS: JUST SAVE THE PROFILE
    instance.userprofile.save()

