from django.urls import path

from . import views

urlpatterns = [
    path('users/', views.UsersList.as_view(), name="users-list"),
    path('users/<id>', views.UsersList.as_view(), name="users-list"),
    path('login/',
         views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('login/refresh/',
         views.TokenRefreshView.as_view(),
         name='token_refresh'),
]