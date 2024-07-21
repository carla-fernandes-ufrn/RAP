from django.urls import path

from django.contrib.auth import views as auth_views
from Usuario import views

app_name = 'usuario'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='Usuario/login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('cadastrar/', views.Cadastrar.as_view(), name="cadastrar"),
    path('completar-cadastro/', views.completar_cadastro, name="completar_cadastro"),
    path('editar/<int:pk>', views.Editar.as_view(), name = 'editar'),
    path('alterar-avatar/<int:pk>/<int:novo>', views.alterar_avatar, name = 'alterar_avatar'),
    path('alterar-senha/<int:pk>', views.AlterarSenha.as_view(), name = 'alterar_senha'),
    path('listar-ativos/', views.listar_ativos, name='listar_ativos'),
    path('listar-inativos/', views.listar_inativos, name='listar_inativos'),
    path('detalhes/<int:pk>', views.Detalhes.as_view(), name='detalhes'),
    path('mudar-status/<int:pk>', views.mudar_status, name='mudar_status'),
    path('mudar-status-admin/<int:pk>', views.mudar_status_admin, name='mudar_status_admin'),
    path('deletarUsuario/<int:pk>', views.DeletarUser.as_view(), name='deletar'),
]