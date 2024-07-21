from django.urls import path

from Acoes import views

app_name = 'acoes'

urlpatterns = [
    path('criar/', views.CriarAcao.as_view(), name='criar'),
    path('deletar/<int:pk>/', views.deletar, name='deletar'),
    path('detalhes/<int:pk>/', views.DetalhesAcao.as_view(), name='detalhes'),
    path('editar/<int:pk>/', views.EditarAcao.as_view(), name='editar'),
    path('listar/<int:pk>', views.ListarAcoesUsuario.as_view(), name='listar_usuario'),
    path('listar/', views.ListarTodasAcoes.as_view(), name='listar'),
    path('alterar-status-acao/<int:pk>', views.alterar_status_acao, name='alterar_status_acao'),

    path('deletar-mensagem/<int:pk>/', views.deletar_mensagem, name='deletar_mensagem'),

    path('editar-midia/<int:pk>/', views.editar_midia, name='editar_midia'),
    path('deletar-midia/<int:pk>/', views.deletar_midia, name='deletar_midia'),

]