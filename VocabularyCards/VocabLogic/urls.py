from django.urls import path
from . import views


urlpatterns = [

    path('', views.home, name='home'),
    path('viewCards/', views.viewCards, name='viewCards'),
    path('viewCard/<int:card_id>', views.viewCard, name='viewCard'),
    path('createPage/', views.createPage, name='createPage'),
    path('addCard/', views.addCard, name='addCard'),
    path('searchAdd/<str:word>/<str:definition>/<str:example>', views.searchAdd, name='searchAdd'),
    path('deleteCard/<int:card_id>/', views.deleteCard, name='deleteCard'),
    path('deleteDef/<int:def_id>/', views.deleteDef, name='deleteDef'),
    path('editWordPage/<int:card_id>', views.editWordPage, name='editWordPage'),
    path('<int:card_id>/editWord/', views.editWord, name='editWord'),
    path('editDefPage/<int:def_id>', views.editDefPage, name='editDefPage'),
    path('editDef/<int:def_id>', views.editDef, name='editDef'),



]
