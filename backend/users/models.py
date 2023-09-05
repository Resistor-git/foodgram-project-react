from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        help_text='Email'
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        help_text='Name'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        help_text='Surname'
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,  # ? или через User = get_user_model()
        on_delete=models.CASCADE,
        related_name='follower',  # subscriptions
        verbose_name='Follower (кто подписан)'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',  # followers
        verbose_name='Content author (на кого подписан)'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_subscription')
        ]
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    def __str__(self):
        return f'{self.user} is subscribed to {self.author}'
