from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    otp = models.CharField(max_length=100, null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    wallet_address = models.CharField(max_length=1000, unique=True, default="None")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.username and self.email:
            self.username = self.email.split('@')[0]
        super(User, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to="user_folder", default=settings.DEFAULT_AVATAR, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    country = models.CharField(max_length=100, null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.full_name:
            return str(self.full_name)
        else:
            return str(self.user.full_name)
        
    
    def save(self, *args, **kwargs):
        # Sync user details to profile
        if not self.full_name or self.full_name == "":
            self.full_name = self.user.full_name or self.user.username
        
        # If user has a wallet address, ensure it's synced
        if self.user.wallet_address and self.user.wallet_address != "None":
            self.user.wallet_address = self.user.wallet_address
            
        super(Profile, self).save(*args, **kwargs)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            full_name=instance.full_name or instance.username,
            image=settings.DEFAULT_AVATAR
        )

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)