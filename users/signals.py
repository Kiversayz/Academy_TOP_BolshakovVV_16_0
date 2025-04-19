from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def assign_default_permissions(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'CREATOR':
            # Назначение прав создателя
            pass