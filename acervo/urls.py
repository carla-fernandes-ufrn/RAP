# acervo/urls.py

from django.urls import path
from . import views

app_name = 'acervo'

urlpatterns = [
    path('', views.listar_acervo, name='acervo'),
    path('listar/', views.listar_acervo, name='listar_acervo'),
    path('criar/', views.criar_acervo, name='criar'),
    path('<int:pk>/', views.detalhes_acervo, name='detalhes_acervo'),
    path('editar/<int:pk>/', views.editar_acervo, name='editar'),
    path('listar_usuario/<int:pk>/', views.listar_acervo_usuario, name='acervo_usuario'),
]
