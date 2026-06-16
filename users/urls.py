from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('', views.home, name="home"),

    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),

    path('api/register/', views.register_api, name="register_api"),
    path('api/profile/', views.profile, name="profile"),

    path('api/token/', TokenObtainPairView.as_view()),
]