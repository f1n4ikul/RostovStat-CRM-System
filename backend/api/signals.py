from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        # Используем get_or_create вместо простого create
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Для существующих пользователей проверяем наличие профиля
        profile, created_now = UserProfile.objects.get_or_create(user=instance)
        if not created_now:
            profile.save()