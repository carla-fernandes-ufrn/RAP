from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from django.http import JsonResponse

from django.views import generic
from django.urls import reverse_lazy

from django.views.decorators.csrf import csrf_exempt

from Disciplina.models import Disciplina, Conteudo, SugestaoDisciplina, SugestaoConteudo
from Usuario.models import Usuario

# class CriarDisciplina(generic.CreateView):
#     model = Disciplina
#     fields = ['name']
#     template_name = "Disciplina/criar.html"
#     success_url = reverse_lazy('plano_aula:listar')


def listar(request):
    disciplinas = Disciplina.objects.filter(status="Ativo")
    conteudos = Conteudo.objects.filter(status="Ativo")

    informacoes = {
        'lista_disciplinas': disciplinas,
        'lista_conteudos': conteudos,
    }

    return render(request, "Disciplina/listar.html", informacoes)

def listar_conteudos(request):
    nome = request.GET.get('nome')
    disciplina = Disciplina.objects.get(nome=nome)
    conteudos = Conteudo.objects.filter(disciplina=disciplina).values_list()

    return finalizar_requisicao_api(list(conteudos))

def listar_sugestoes(request, tipo):
    sugestoes_disciplina = SugestaoDisciplina.objects.filter(status="A")
    sugestoes_conteudo = SugestaoConteudo.objects.filter(status="A")
    disciplinas = Disciplina.objects.filter(status="Ativo")
    conteudos = Conteudo.objects.filter(status="Ativo")

    informacoes = {
        'sugestoes_disciplina': sugestoes_disciplina,
        'sugestoes_conteudo': sugestoes_conteudo,
        'lista_disciplinas': disciplinas,
        'lista_conteudos': conteudos,
        'tipo': tipo,
    }

    return render(request, "Disciplina/listar_sugestoes.html", informacoes)

def listar_sugestoes_usuario(request, pk):
    usuario = Usuario.objects.get(pk=pk)
    sugestoes_disciplina_em_aberto = SugestaoDisciplina.objects.filter(status="A", usuario = usuario)
    sugestoes_disciplina_aceita = SugestaoDisciplina.objects.filter(status="B", usuario = usuario)
    sugestoes_disciplina_negada = SugestaoDisciplina.objects.filter(status="C", usuario = usuario)
    sugestoes_conteudo_em_aberto = SugestaoConteudo.objects.filter(status="A", usuario = usuario)
    sugestoes_conteudo_aceito = SugestaoConteudo.objects.filter(status="B", usuario = usuario)
    sugestoes_conteudo_negado = SugestaoConteudo.objects.filter(status="C", usuario = usuario)

    informacoes = {
        'sugestoes_disciplina_em_aberto': sugestoes_disciplina_em_aberto,
        'sugestoes_disciplina_aceita': sugestoes_disciplina_aceita,
        'sugestoes_disciplina_negada': sugestoes_disciplina_negada,
        'sugestoes_conteudo_em_aberto': sugestoes_conteudo_em_aberto,
        'sugestoes_conteudo_aceito': sugestoes_conteudo_aceito,
        'sugestoes_conteudo_negado': sugestoes_conteudo_negado,
    }

    return render(request, "Disciplina/listar_sugestoes_usuario.html", informacoes)

@csrf_exempt
def analisar_sugestoes_disciplina(request):
    lista_disciplinas_aceitas = request.POST.getlist('lista_disciplinas_aceitas[]')
    lista_disciplinas_negadas = request.POST.getlist('lista_disciplinas_negadas[]')

    for pk in lista_disciplinas_aceitas:
        sugestao = SugestaoDisciplina.objects.get(id=int(pk))
        if (len(Disciplina.objects.filter(nome = sugestao.nome)) == 0) : 
            nova_disciplina = Disciplina(nome = sugestao.nome)
            nova_disciplina.save()
            sugestao.status = 'B'
            sugestao.save()
        else:
            sugestao.status = 'C'
            sugestao.save()
    
    for pk in lista_disciplinas_negadas:
        sugestao = SugestaoDisciplina.objects.get(id=int(pk))
        sugestao.status = 'C'
        sugestao.save()

    return redirect('disciplina:listar_sugestoes', tipo=0)

@csrf_exempt
def analisar_sugestoes_conteudo(request):
    lista_conteudos_aceitos = request.POST.getlist('lista_conteudos_aceitos[]')
    lista_conteudos_negados = request.POST.getlist('lista_conteudos_negados[]')

    for pk in lista_conteudos_aceitos:
        sugestao = SugestaoConteudo.objects.get(id=int(pk))
        if (len(Conteudo.objects.filter(nome = sugestao.nome, disciplina = sugestao.disciplina)) == 0): 
            novo_conteudo = Conteudo(nome = sugestao.nome, disciplina = sugestao.disciplina)
            novo_conteudo.save()
            sugestao.status = 'B'
            sugestao.save()
        else:
            sugestao.status = 'C'
            sugestao.save()
    
    for pk in lista_conteudos_negados:
        sugestao = SugestaoConteudo.objects.get(id=int(pk))
        sugestao.status = 'C'
        sugestao.save()

    return redirect('disciplina:listar_sugestoes', tipo=1)

@csrf_exempt
def sugerir_disciplina(request):
    nome = request.POST.get('nome')
    usuario = Usuario.objects.get(username=request.user.username)
    sugestao_disciplina = SugestaoDisciplina(nome = nome, usuario = usuario)
    sugestao_disciplina.save()
    
    return finalizar_requisicao_api('Sucesso')

@csrf_exempt
def sugerir_conteudo(request):
    nome = request.POST.get('nome')
    nome_disciplina = request.POST.get('disciplina')
    usuario = Usuario.objects.get(username=request.user.username)
    disciplina = Disciplina.objects.get(nome = nome_disciplina)
    sugestao_conteudo = SugestaoConteudo(nome = nome, usuario = usuario, disciplina = disciplina)
    sugestao_conteudo.save()
    
    return finalizar_requisicao_api('Sucesso')

def definir_status_sugestao_disciplina(request, aceitar, id):
    sugestao_disciplina = SugestaoDisciplina.objects.get(id=id)

    if (aceitar == 1):
        sugestao_disciplina.status = "B"
        sugestao_disciplina.save()

        disciplina = Disciplina(nome = sugestao_disciplina.nome)
        disciplina.save()
    else:
        sugestao_disciplina.status = "C"
        sugestao_disciplina.save()

    return redirect('disciplina:listar_sugestoes')

def ler_numero_sugestoes(request):
    qnt_sugestoes_disciplina = len(SugestaoDisciplina.objects.filter(status = 'A'))
    qnt_sugestoes_conteudo = len(SugestaoConteudo.objects.filter(status = 'A'))

    resposta = qnt_sugestoes_disciplina + qnt_sugestoes_conteudo
    return JsonResponse({"qnt":resposta}, status = 200)

def ler_id_conteudo(request):
    nome_disciplina = request.GET.get('disciplina')
    nome_conteudo = request.GET.get('conteudo')
    
    disciplina = Disciplina.objects.get(nome=nome_disciplina)
    conteudo = Conteudo.objects.get(nome=nome_conteudo, disciplina=disciplina)

    id_conteudo = conteudo.id
    return JsonResponse({"id":id_conteudo}, status = 200)


def finalizar_requisicao_api(response_data):
    response_data = response_data

    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )
