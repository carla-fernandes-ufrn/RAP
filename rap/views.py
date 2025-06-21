from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from Usuario.models import Usuario
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

def buscar(request):
    termo = request.GET.get('q', '')

    planos = PlanoAula.objects.filter(
        Q(titulo__icontains=termo) |
        Q(conteudos__nome__icontains=termo) |
        Q(conteudos__disciplina__nome__icontains=termo)
    ).distinct()

    acoes = Acoes.objects.filter(
        Q(titulo__icontains=termo) |
        Q(local__icontains=termo)
    ).distinct()

    usuarios = Usuario.objects.filter(
        Q(first_name__icontains=termo) |
        Q(last_name__icontains=termo)
    ).distinct()

    # Junta tudo em uma lista só e adiciona o tipo
    resultados = []

    for p in planos:
        resultados.append({'tipo': 'plano', 'obj': p})
    for a in acoes:
        resultados.append({'tipo': 'acao', 'obj': a})
    for u in usuarios:
        resultados.append({'tipo': 'usuario', 'obj': u})

    # Paginação
    paginator = Paginator(resultados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'termo': termo
    }

    return render(request, 'base/busca.html', context)


class BuscarAjaxView(View):
    def get(self, request):
        termo = request.GET.get('q', '')

        planos = list(PlanoAula.objects.filter(titulo__icontains=termo).values('id', 'titulo')[:10])
        acoes = list(Acoes.objects.filter(titulo__icontains=termo).values('id', 'titulo')[:10])
        usuarios = list(Usuario.objects.filter(first_name__icontains=termo).values('id', 'first_name', 'last_name')[:10])

        return JsonResponse({
            'planos': planos,
            'acoes': acoes,
            'usuarios': usuarios,
        })

def encontrar_planos_aula_disciplina(planos_aula, disciplinas):

    print(disciplinas)

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
            if (disciplina in disciplinas):
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