from django.urls import path
from . import views


urlpatterns = [

    path('', views.home, name='home'),
    path('viewCards/', views.viewCards, name='viewCards'),
    path('createPage/', views.createPage, name='createPage'),
    path('addCard/', views.addCard, name='addCard'),

]
