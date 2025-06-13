from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from django.core.exceptions import PermissionDenied
import json
from django.http import JsonResponse

from django.views import generic
from django.urls import reverse_lazy

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test

from Disciplina.models import Disciplina, Conteudo, SugestaoDisciplina, SugestaoConteudo
from PlanoAula.models import PlanoAula
from rap.views import encontrar_planos_aula_disciplina
from Usuario.models import Usuario

# class CriarDisciplina(generic.CreateView):
#     model = Disciplina
#     fields = ['name']
#     template_name = "Disciplina/criar.html"
#     success_url = reverse_lazy('plano_aula:listar')

@login_required
def listar(request):
    planos_aula = PlanoAula.objects.filter(status=True)
    
    disciplinas = Disciplina.objects.filter(status="Ativo")
    conteudos = Conteudo.objects.filter(status="Ativo")

    informacoes = {
        'lista_disciplinas': encontrar_planos_aula_disciplina(planos_aula, list(disciplinas)),
        'lista_conteudos': conteudos,
    }

    return render(request, "Disciplina/listar.html", informacoes)

@login_required
def listar_conteudos(request):
    nome = request.GET.get('nome')
    disciplina = Disciplina.objects.get(nome=nome)
    conteudos = Conteudo.objects.filter(disciplina=disciplina).values_list()

    return HttpResponse(
        json.dumps(list(conteudos)),
        content_type="application/json"
    )

@login_required
def listar_sugestoes(request):
    if (request.user.is_superuser):
        sugestoes_disciplina = SugestaoDisciplina.objects.filter(status="A")
        sugestoes_conteudo = SugestaoConteudo.objects.filter(status="A")
        disciplinas = Disciplina.objects.filter(status="Ativo")
        conteudos = Conteudo.objects.filter(status="Ativo")

        informacoes = {
            'sugestoes_disciplina': sugestoes_disciplina,
            'sugestoes_conteudo': sugestoes_conteudo,
            'lista_disciplinas': disciplinas,
            'lista_conteudos': conteudos,
        }

        return render(request, "Disciplina/listar_sugestoes.html", informacoes)
    else:
        raise PermissionDenied()

@login_required
def listar_sugestoes_usuario(request, pk):
    if (request.user.id == pk):
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
    else:
        raise PermissionDenied()

@csrf_exempt
@login_required
def analisar_sugestoes_disciplina(request):
    lista_disciplinas_aceitas = request.POST.getlist('lista_disciplinas_aceitas[]')
    lista_disciplinas_negadas = request.POST.getlist('lista_disciplinas_negadas[]')

    for pk in lista_disciplinas_aceitas:
        sugestao = SugestaoDisciplina.objects.get(id=int(pk))
        disciplina_existente = Disciplina.objects.filter(nome__iexact=sugestao.nome).first()

        if not disciplina_existente:
            # Não existe disciplina com esse nome: criar nova
            nova_disciplina = Disciplina(nome=sugestao.nome)
            nova_disciplina.save()
            sugestao.status = 'B'  # Aprovada
        else:
            if disciplina_existente.status == 'Inativo':
                # Já existe, mas está inativa → reativar
                disciplina_existente.status = 'Ativo'
                disciplina_existente.save()
                sugestao.status = 'B'  # Aprovada
            else:
                # Já existe e está ativa → marcar como conflituosa
                sugestao.status = 'C'  # Conflito

        sugestao.save()
    
    for pk in lista_disciplinas_negadas:
        sugestao = SugestaoDisciplina.objects.get(id=int(pk))
        sugestao.status = 'C'
        sugestao.save()

    return redirect('disciplina:listar_sugestoes')

@csrf_exempt
@login_required
def analisar_sugestoes_conteudo(request):
    lista_conteudos_aceitos = request.POST.getlist('lista_conteudos_aceitos[]')
    lista_conteudos_negados = request.POST.getlist('lista_conteudos_negados[]')

    for pk in lista_conteudos_aceitos:
        sugestao = SugestaoConteudo.objects.get(id=int(pk))
        conteudo_existente = Conteudo.objects.filter(
            nome__iexact=sugestao.nome,
            disciplina=sugestao.disciplina
        ).first()

        if not conteudo_existente:
            # Não existe conteúdo com esse nome na disciplina → criar novo
            novo_conteudo = Conteudo(nome=sugestao.nome, disciplina=sugestao.disciplina)
            novo_conteudo.save()
            sugestao.status = 'B'  # Aprovado
        else:
            if conteudo_existente.status == 'Inativo':
                # Existe, mas está inativo → reativar
                conteudo_existente.status = 'Ativo'
                conteudo_existente.save()
                sugestao.status = 'B'  # Aprovado
            else:
                # Já existe e está ativo → conflito
                sugestao.status = 'C'

        sugestao.save()
    
    for pk in lista_conteudos_negados:
        sugestao = SugestaoConteudo.objects.get(id=int(pk))
        sugestao.status = 'C'
        sugestao.save()

    return redirect('disciplina:listar_sugestoes')

@csrf_exempt
@login_required
def sugerir_disciplina(request):
    nome = request.POST.get('nome')
    usuario = Usuario.objects.get(username=request.user.username)
    sugestao_disciplina = SugestaoDisciplina(nome = nome, usuario = usuario)
    sugestao_disciplina.save()
    
    return HttpResponse(
        json.dumps("Sucesso"),
        content_type="application/json"
    )

@csrf_exempt
@login_required
def sugerir_conteudo(request):
    nome = request.POST.get('nome')
    nome_disciplina = request.POST.get('disciplina')
    usuario = Usuario.objects.get(username=request.user.username)
    disciplina = Disciplina.objects.get(nome = nome_disciplina)
    sugestao_conteudo = SugestaoConteudo(nome = nome, usuario = usuario, disciplina = disciplina)
    sugestao_conteudo.save()
    
    return HttpResponse(
        json.dumps("Sucesso"),
        content_type="application/json"
    )

@login_required
def definir_status_sugestao_disciplina(request, aceitar, id):
    if (request.user.is_superuser):
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
    else:
        raise PermissionDenied()

@login_required
def ler_numero_sugestoes(request):
    qnt_sugestoes_disciplina = len(SugestaoDisciplina.objects.filter(status = 'A'))
    qnt_sugestoes_conteudo = len(SugestaoConteudo.objects.filter(status = 'A'))

    resposta = qnt_sugestoes_disciplina + qnt_sugestoes_conteudo
    return JsonResponse({"qnt":resposta}, status = 200)

@login_required
def editar_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)

    if request.method == 'POST':
        novo_nome = request.POST.get('nome')

        if not novo_nome:
            return JsonResponse({'success': False, 'error': 'Nome não pode ser vazio.'})

        # Verifica se já existe outra disciplina com o mesmo nome (ignorando maiúsculas/minúsculas)
        existe = Disciplina.objects.filter(nome__iexact=novo_nome).exclude(pk=disciplina.pk).exists()
        if existe:
            return JsonResponse({'success': False, 'error': 'Já existe uma disciplina com esse nome.'})

        disciplina.nome = novo_nome
        disciplina.save()
        return JsonResponse({'success': True, 'nome': disciplina.nome})

    # Se GET, retorna dados para preencher o modal
    return JsonResponse({
        'id': disciplina.id,
        'nome': disciplina.nome,
    })

@login_required
def editar_conteudo(request, pk):
    conteudo = get_object_or_404(Conteudo, pk=pk)

    if request.method == 'POST':
        novo_nome = request.POST.get('nome')

        if not novo_nome:
            return JsonResponse({'success': False, 'error': 'Nome não pode ser vazio.'})

        # Verifica se já existe outro conteúdo com o mesmo nome na mesma disciplina
        existe = Conteudo.objects.filter(
            disciplina=conteudo.disciplina,
            nome__iexact=novo_nome
        ).exclude(pk=conteudo.pk).exists()

        if existe:
            return JsonResponse({
                'success': False,
                'error': 'Já existe um conteúdo com esse nome nesta disciplina.'
            })

        conteudo.nome = novo_nome
        conteudo.save()
        return JsonResponse({'success': True, 'nome': conteudo.nome})

    return JsonResponse({
        'id': conteudo.id,
        'nome': conteudo.nome,
        'disciplina': conteudo.disciplina.nome
    })

@login_required
def inativar_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    disciplina.status = 'Inativo'
    disciplina.save()
    return JsonResponse({'success': True})

@login_required
def inativar_conteudo(request, pk):
    conteudo = get_object_or_404(Conteudo, pk=pk)
    conteudo.status = 'Inativo'
    conteudo.save()
    return JsonResponse({'success': True})

@login_required
def ler_id_conteudo(request):
    nome_disciplina = request.GET.get('disciplina')
    nome_conteudo = request.GET.get('conteudo')
    
    disciplina = Disciplina.objects.get(nome=nome_disciplina)
    conteudo = Conteudo.objects.get(nome=nome_conteudo, disciplina=disciplina)

    id_conteudo = conteudo.id
    return JsonResponse({"id":id_conteudo}, status = 200)

@login_required
def finalizar_requisicao_api(response_data):
    response_data = response_data

    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )
