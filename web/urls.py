from django.urls import path
from . import views

urlpatterns = [
    # --- основные ---
    path('',         views.index,       name='index'),

    # --- auth ---
    path('login/',   views.login_view,  name='web-login'),
    path('logout/',  views.logout_view, name='web-logout'),
    path('signup/',  views.sign_up,     name='web-signup'),

    # --- карточки ---
    path('card/',                    views.my_card,     name='web-my_card'),
    path('card/create/',             views.card_create, name='web-card_create'),
    path('card/edit/',               views.card_edit,   name='web-card_edit'),
    path('card/delete/',             views.card_delete, name='web-card_delete'),
    path('card/user/<int:user_id>/', views.card_view,   name='web-card_view'),
]