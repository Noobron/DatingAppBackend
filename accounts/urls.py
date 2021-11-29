from django.urls import path

from . import views

urlpatterns = [
    path('login/',
         views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('login/refresh/',
         views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('logout/', views.deleteJWTToken, name='token_delete'),
    path('register/', views.register, name='register_user'),
    path('users/', views.get_users, name='get_users_list'),
    path('users/<name>', views.get_users, name='get_user'),
    path('get-photos/<name>', views.get_photos, name='get_photos'),
    path('add-photo/', views.add_photo, name='add_photo'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]