from django.urls import path

from PlanoAula import views

#from .views import deletar

app_name = 'plano_aula'

urlpatterns = [
    path('criar/', views.criar, name='criar'),

    path('deletar/<int:pk>/', views.Deletar.as_view(), name='deletar'),
    path('detalhes/<int:pk>/', views.Detalhe.as_view(), name='detalhes'),
    path('programacao/<int:pk>/', views.Programacao.as_view(), name='programacao'),
    path('editar/<int:pk>/', views.Editar.as_view(), name='editar'),
    path('listar/', views.ListarPlanosAulaFiltrados.as_view(), name='listar'),
    path('listar/<int:pk>', views.ListarPlanosAulaFiltradosUsuario.as_view(), name='listar_usuario'),
    path('listar-favoritos/<int:pk>', views.ListarPlanosAulaFiltradosFavoritos.as_view(), name='listar_favoritos'),
    path('listar-executados/<int:pk>', views.ListarPlanosAulaFiltradosExecutados.as_view(), name='listar_executados'),
    path('programacao/<int:pk>/', views.Programacao.as_view(), name='programacao'),

    path('marcar-favorito/<int:plano_aula>/<int:usuario>/', views.marcar_favorito, name="marcar_favorito"),
    path('marcar-executado/<int:plano_aula>/<int:usuario>/', views.marcar_executado, name="marcar_executado"),
]