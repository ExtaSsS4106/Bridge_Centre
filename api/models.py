from django.db import models
from django.contrib.auth.models import User


class profiles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='user')


class cards(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name='card',     # теперь user.card вместо user.cards_set
        unique=True,             # явно; для OneToOne и так True, но наглядно
    )
    description = models.TextField()
    requisites = models.JSONField()

    def __str__(self):
        return f"Card #{self.pk} — {self.user.username}"