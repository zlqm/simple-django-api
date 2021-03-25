from django.urls import path
from . import views

urlpatterns = [
    path('basic_auth', views.BasicAuthView.as_view()),
    path('auth', views.AuthView.as_view()),
    path('blogs/<int:pk>', views.BlogDetailView.as_view()),
]
