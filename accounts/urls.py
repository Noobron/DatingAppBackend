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
    path('like-user/', views.like_user, name='like_user'),
    path('has-liked/<name>', views.has_liked, name='has_liked'),
    path('unlike-user/', views.unlike_user, name='unlike_user'),
    path('get-photos/<name>', views.get_photos, name='get_photos'),
    path('add-photo/', views.add_photo, name='add_photo'),
    path('delete-photo/', views.delete_photo, name='delete_photo'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]