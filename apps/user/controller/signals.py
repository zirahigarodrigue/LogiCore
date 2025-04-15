from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.user.models import CustomerProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a Customer profile when a user with role 'customer' is created.
    """
    if created and instance.role == 'customer':
        CustomerProfile.objects.create(user=instance)
