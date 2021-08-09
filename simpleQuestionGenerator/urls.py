from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('signIn/', views.signIn, name="signIn"),
    path('signUp/', views.signUp, name="signUp"),
    path('confirmation/', views.confirmation, name="confirmation"),
    path('deleteCreator/',
         views.deleteCreator, name="deleteCreator"),
    path('creatorPage/', views.creatorPage, name="creatorPage"),
    path('signOut/', views.signOut, name="signOut"),
]
