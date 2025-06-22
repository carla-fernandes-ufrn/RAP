from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from Usuario import views

app_name = 'usuario'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='Usuario/login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('perfil/', views.Perfil.as_view(), name="perfil"),
    path('alterar-senha-ajax/', views.alterar_senha_ajax, name='alterar_senha_ajax'),
    path('cadastrar/', views.Cadastrar.as_view(), name="cadastrar"),
    path('completar-cadastro/', views.completar_cadastro, name="completar_cadastro"),
    path('editar/<int:pk>', views.Editar.as_view(), name = 'editar'),
    path('alterar-avatar/<int:pk>/<int:novo>', views.alterar_avatar, name = 'alterar_avatar'),
    path('alterar-senha/<int:pk>', views.AlterarSenha.as_view(), name = 'alterar_senha'),
    path('listar-ativos/', views.ListarAtivos.as_view(), name='listar_ativos'),
    path('listar-inativos/', views.listar_inativos, name='listar_inativos'),
    path('detalhes/<int:pk>', views.Detalhes.as_view(), name='detalhes'),
    path('mudar-status/<int:pk>', views.mudar_status, name='mudar_status'),
    path('mudar-status-admin/<int:pk>', views.mudar_status_admin, name='mudar_status_admin'),
    path('deletarUsuario/<int:pk>', views.DeletarUser.as_view(), name='deletar'),
    path('planos_aula/<int:pk>', views.ler_informacoes_plano_aula, name="informacoes_plano_aula"),
    path('acoes/<int:pk>', views.ler_informacoes_acoes, name="informacoes_acoes"),
    path(
        'esqueceu-senha/', 
        auth_views.PasswordResetView.as_view(
            template_name='Usuario/esqueceu_senha.html', 
            success_url=reverse_lazy('usuario:password_reset_done')
        ), 
        name='password_reset'
    ),
    path(
        'esqueceu-senha/enviado/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='Usuario/esqueceu_senha_enviado.html'
        ), 
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='Usuario/reset_senha_confirm.html', 
            success_url=reverse_lazy('usuario:password_reset_complete')
        ), 
        name='password_reset_confirm'
    ),
    path(
        'reset/sucesso/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='Usuario/reset_senha_sucesso.html'
        ), 
        name='password_reset_complete'),
]