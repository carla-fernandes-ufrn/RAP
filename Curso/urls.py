from django.urls import path

from Curso import views

app_name = 'curso'

urlpatterns = [
    path('criar/', views.criar, name='criar'),
    # path('deletar/<int:pk>/', views.Deletar.as_view(), name='deletar'),
    # path('detalhes/<int:pk>/', views.Detalhe.as_view(), name='detalhes'),
    # path('editar/<int:pk>/', views.Editar.as_view(), name='editar'),
    # path('listar/<int:pk>', views.listar_usuario, name='listar_usuario'),
    # path('listar/', views.ListarPlanosAulaFiltrados.as_view(), name='listar'),
]