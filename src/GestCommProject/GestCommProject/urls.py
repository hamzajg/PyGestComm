"""GestCommProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenBlacklistView, TokenObtainPairView, TokenRefreshView,
    TokenVerifyView)
from GestCommApp import views

urlpatterns = [
    path('api/client', views.ClientList.as_view()),
    path('api/client/<int:pk>', views.ClientDetail.as_view()),
    path('api/article', views.ArticleList.as_view()),
    path('api/article/<int:pk>', views.ArticleDetail.as_view()),
    path('api/devis', views.DevisList.as_view()),
    path('api/devis/<int:pk>', views.DevisDetail.as_view()),
    path('api/devis/<int:pk>/convertir', views.DevisConvertir.as_view()),
    path('api/facture', views.FactureList.as_view()),
    path('api/facture/<int:pk>', views.FactureDetail.as_view()),
    path('api/bonliv', views.BonLivList.as_view()),
    path('api/bonliv/<int:pk>', views.BonLivDetail.as_view()),
    path('api/assistant/ask', views.AssistantAsk.as_view()),
    path('api/me', views.MeView.as_view()),
    path('api/me/password', views.PasswordChangeView.as_view()),
    path('api/token', TokenObtainPairView.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view()),
    path('api/token/verify', TokenVerifyView.as_view()),
    path('api/token/logout', TokenBlacklistView.as_view()),
    path('admin/', admin.site.urls),
]
