from django.urls import path

from PlanoAula import views

#from .views import deletar

app_name = 'plano_aula'

urlpatterns = [
    path('criar/', views.criar, name='criar'),
    
    path('detalhes/<int:pk>/', views.Detalhe.as_view(), name='detalhes'),
    path('editar-midia/<int:pk>/', views.editar_midia, name='editar_midia'),
    path('deletar-midia/<int:tipo>/<int:pk>/', views.deletar_midia, name='deletar_midia'),
    path('editar/<int:pk>/', views.editar, name='editar'),
    path('deletar-mensagem/<int:pk>/', views.deletar_mensagem, name='deletar_mensagem'),

    path('desabilitar/<int:pk>/', views.desabilitar, name='desabilitar'),
    path('deletar/<int:pk>/', views.Deletar.as_view(), name='deletar'),
    
    path('listar/', views.ListarPlanosAulaFiltrados.as_view(), name='listar'),
    path('listar/<int:pk>', views.ListarPlanosAulaFiltradosUsuario.as_view(), name='listar_usuario'),
    path('listar-favoritos/<int:pk>', views.ListarPlanosAulaFiltradosFavoritos.as_view(), name='listar_favoritos'),
    path('listar-executados/<int:pk>', views.ListarPlanosAulaFiltradosExecutados.as_view(), name='listar_executados'),

    path('marcar-favorito/<int:plano_aula>/<int:usuario>/', views.marcar_favorito, name="marcar_favorito"),
    path('marcar-executado/<int:plano_aula>/<int:usuario>/', views.marcar_executado, name="marcar_executado"),
]