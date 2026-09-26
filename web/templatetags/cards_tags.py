from django import template
from api.models import cards

register = template.Library()


@register.simple_tag
def get_all_cards(limit=None):
    """Возвращает queryset карточек. Использование в шаблоне:
       {% get_all_cards 12 as cards %}
    """
    qs = cards.objects.select_related('user').order_by('-id')
    if limit:
        qs = qs[:int(limit)]
    return qs


@register.simple_tag
def get_user_card(user):
    """Возвращает карточку конкретного пользователя (или None)."""
    if not user or not user.is_authenticated:
        return None
    return cards.objects.filter(user=user).first()