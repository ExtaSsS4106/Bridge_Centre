from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from .views import GetCards, EditCard
from .views import (
    RegisterView, ProfileView, LogoutView,
    AllUsers,AmIsuperUser, ProfileInfo, ErrorResponse
)
urlpatterns = [
    path('', ErrorResponse.as_view(), name='error-response'),
    
    path('profile-info/', ProfileInfo.as_view(), name='profile-info'),
    
    path('amisuperuser/', AmIsuperUser.as_view(), name='register'),

    path('register/', RegisterView.as_view(), name='register'),
    
    path('profile/', ProfileView.as_view(), name='profile'),
    
    path('logout/', LogoutView.as_view(), name='logout'),
    
    path('all-users/', AllUsers.as_view(), name='all-users'),

    path('api/cards/',      GetCards.as_view(), name='cards-list'),
    path('api/cards/edit/', EditCard.as_view(), name='card-edit'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
