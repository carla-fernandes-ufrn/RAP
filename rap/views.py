from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Disciplina.models import Disciplina, Conteudo
from PlanoAula.models import PlanoAula, LikePlanoAula, ExecucaoPlanoAula
from Acoes.models import Acoes

@login_required
def home(request):

    if (not request.user.first_name or not request.user.last_name):
        return redirect('usuario:completar_cadastro')
    
    planos_aula = PlanoAula.objects.all()
    conteudos = list(Conteudo.objects.filter(status='Ativo'))
    disciplinas = list(Disciplina.objects.filter(status='Ativo'))
    acoes = list(Acoes.objects.filter(status=True))

    inf_disciplinas = encontrar_planos_aula_disciplina(planos_aula, disciplinas)
    principais_conteudos = encontrar_principais_conteudos(likes_execucao_por_conteudo(planos_aula, conteudos), 5)
    principais_planos_aula = encontrar_principais_planos_aula(planos_aula, 6)

    # definir_principais_disciplinas(request.user.id)

    principais_acoes = encontrar_principais_acoes(acoes, 6)

    informacoes = {
        'lista_planos_aula': planos_aula[:10],
        'principais_conteudos': principais_conteudos,
        'principais_planos_aula': principais_planos_aula,
        'inf_disciplinas': inf_disciplinas,
        'principais_acoes': principais_acoes,
    }

    return render(request, "home.html", informacoes)

    # return render(request, "Base/home.html")

def encontrar_planos_aula_disciplina(planos_aula, disciplinas):

    inf_disciplinas = []

    for disciplina in disciplinas:
        informacoes = []
        informacoes.append(disciplina)
        informacoes.append(0)
        inf_disciplinas.append(informacoes)

    for plano_aula in planos_aula:
        disciplinas_pa = []
        for conteudo in plano_aula.conteudos.all():
            if conteudo.disciplina not in disciplinas_pa:
                disciplinas_pa.append(conteudo.disciplina)
        for disciplina in disciplinas_pa:
            indice = disciplinas.index(disciplina)
            inf_disciplinas[indice][1] += 1
    
    return inf_disciplinas

def encontrar_principais_planos_aula(planos_aula, quantidade):

    inf_planos_aula = []

    for plano_aula in planos_aula:
        likes = list(LikePlanoAula.objects.filter(plano_aula=plano_aula).values_list('usuario', flat=True))
        execucoes = list(ExecucaoPlanoAula.objects.filter(plano_aula=plano_aula).values_list('usuario', flat=True))
        quantidade_likes_execucoes = len(set(likes + execucoes))
        inf_planos_aula.append([plano_aula, quantidade_likes_execucoes])
    
    inf_planos_aula.sort(key = lambda x: x[1], reverse=True)
    
    return inf_planos_aula[0:quantidade]

def encontrar_principais_conteudos(inf_conteudos, quantidade):
    inf_conteudos.sort(key = lambda x: x[1], reverse=True)
    return inf_conteudos[0:quantidade]

def encontrar_principais_acoes(acoes, quantidade):
    return acoes[0:quantidade]

def likes_execucao_por_conteudo(planos_aula, conteudos):
    likes = LikePlanoAula.objects.all()
    execucoes = ExecucaoPlanoAula.objects.all()

    inf_conteudos = []

    for conteudo in conteudos:
        informacoes = []
        informacoes.append(conteudo)
        informacoes.append(0)
        inf_conteudos.append(informacoes)

    for plano_aula in planos_aula:
        likes = list(LikePlanoAula.objects.filter(plano_aula=plano_aula).values_list('usuario', flat=True))
        execucoes = list(ExecucaoPlanoAula.objects.filter(plano_aula=plano_aula).values_list('usuario', flat=True))
        quantidade_likes_execucoes = len(set(likes + execucoes))
        for indice, conteudo in enumerate(conteudos):
            if conteudo in plano_aula.conteudos.all():
                inf_conteudos[indice][1] += quantidade_likes_execucoes
    
    return inf_conteudos