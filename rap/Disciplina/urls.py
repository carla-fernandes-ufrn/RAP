from django.urls import path

from Disciplina import views

app_name = 'disciplina'

urlpatterns = [
    # path('criar_disciplina/', views.CriarDisciplina.as_view(), name="criar_disciplina"),
    # path('criar_conteudo/', views.CriarConteudo.as_view(), name="criar_conteudo"),
    # path('editar_disciplina/<int:pk>/', views.EditarDisciplina.as_view(), name="editar_disciplina"),
    # path('editar_conteudo/<int:pk>/', views.EditarConteudo.as_view(), name="editar_conteudo"),
    path('listar/', views.listar, name="listar"),
    path('listar-conteudos/', views.listar_conteudos, name="listar_conteudos"),
    path('sugerir-disciplina/', views.sugerir_disciplina, name="sugerir_disciplina"),
    path('sugerir-conteudo/', views.sugerir_conteudo, name="sugerir_conteudo"),
    # path('sugerir_disciplina/', views.SugerirDisciplina.as_view(), name="sugerir_disciplina"),
    # path('sugerir_conteudo/', views.SugerirConteudo.as_view(), name="sugerir_conteudo"),

    # Admin
    path('listar-sugestoes/<int:tipo>', views.listar_sugestoes, name="listar_sugestoes"),
    path('analisar-disciplinas/', views.analisar_sugestoes_disciplina, name="analisar_disciplinas"),
    path('analisar-conteudos/', views.analisar_sugestoes_conteudo, name="analisar_conteudos"),
    path('definir-status-sugestao-disciplina/<int:aceitar>/<int:id>', views.definir_status_sugestao_disciplina, name="definir_status_sugestao_disciplina"),

    # Usuários
    path('listar-sugestoes-usuario/<int:pk>', views.listar_sugestoes_usuario, name="listar_sugestoes_usuario"),
    path('numero-sugestoes/', views.ler_numero_sugestoes, name="numero_sugestoes"),

    path('ler-id-conteudo/', views.ler_id_conteudo, name="ler_id_conteudo"),


    # path('deletar/<int:pk>', views.Deletar.as_view(), name="deletar"),
]