
# backend/urls.py
from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    
    path('sign-up/', views.sign_up, name='sign_up'),
    path('logout/', views.logout_view, name='logout'),
    path('login_/', views.login_view, name='login_'),
]