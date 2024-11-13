from django.urls import path

from Disciplina import views

app_name = 'disciplina'

urlpatterns = [
    path('listar/', views.listar, name="listar"),
    path('listar-conteudos/', views.listar_conteudos, name="listar_conteudos"),
    path('sugerir-disciplina/', views.sugerir_disciplina, name="sugerir_disciplina"),
    path('sugerir-conteudo/', views.sugerir_conteudo, name="sugerir_conteudo"),

    # Admin
    path('listar-sugestoes/', views.listar_sugestoes, name="listar_sugestoes"),
    path('analisar-disciplinas/', views.analisar_sugestoes_disciplina, name="analisar_disciplinas"),
    path('analisar-conteudos/', views.analisar_sugestoes_conteudo, name="analisar_conteudos"),
    path('definir-status-sugestao-disciplina/<int:aceitar>/<int:id>', views.definir_status_sugestao_disciplina, name="definir_status_sugestao_disciplina"),

    # Usuários
    path('listar-sugestoes-usuario/<int:pk>', views.listar_sugestoes_usuario, name="listar_sugestoes_usuario"),
    path('numero-sugestoes/', views.ler_numero_sugestoes, name="numero_sugestoes"),

    path('ler-id-conteudo/', views.ler_id_conteudo, name="ler_id_conteudo"),
]