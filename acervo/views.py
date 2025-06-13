# acervo/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Acervo
from .forms import AcervoForm
from django.core.paginator import Paginator

@login_required
def listar_acervo(request):
    # Se quiser filtros, você pode criar um outro formulário ou usar esse mesmo.
    form_filtro = AcervoForm(request.GET or None)
    acervo_items = Acervo.objects.all()

    if form_filtro.is_valid():
        if form_filtro.cleaned_data.get('titulo'):
            acervo_items = acervo_items.filter(titulo__icontains=form_filtro.cleaned_data['titulo'])
        if form_filtro.cleaned_data.get('tipo'):
            acervo_items = acervo_items.filter(tipo=form_filtro.cleaned_data['tipo'])
        if form_filtro.cleaned_data.get('autor'):
            acervo_items = acervo_items.filter(autor__icontains=form_filtro.cleaned_data['autor'])
        if form_filtro.cleaned_data.get('ano'):
            acervo_items = acervo_items.filter(ano=form_filtro.cleaned_data['ano'])
        if form_filtro.cleaned_data.get('licenca_de_uso'):
            acervo_items = acervo_items.filter(licenca_de_uso__icontains=form_filtro.cleaned_data['licenca_de_uso'])

    paginator = Paginator(acervo_items, 10)
    page_number = request.GET.get('page')
    lista_acervos = paginator.get_page(page_number)

    exibir_todos = request.GET.get('listar') == 'todos'

    context = {
        'acervo_items': lista_acervos,
        'form_filtro': form_filtro,
        'exibir_todos': exibir_todos,
        'page_obj': lista_acervos,
    }

    return render(request, 'acervo/listar_acervo.html', context)

@login_required
def criar_acervo(request):
    if request.method == 'POST':
        form = AcervoForm(request.POST, request.FILES)
        if form.is_valid():
            acervo = form.save(commit=False)
            acervo.responsavel = request.user
            acervo.save()
            return redirect('acervo:acervo')
    else:
        form = AcervoForm()
    return render(request, 'acervo/submeter_acervo.html', {'form': form})

@login_required
def detalhes_acervo(request, pk):
    acervo_item = get_object_or_404(Acervo, pk=pk)
    return render(request, 'acervo/detalhes_acervo.html', {'acervo_item': acervo_item})

@login_required
def editar_acervo(request, pk):
    acervo = get_object_or_404(Acervo, pk=pk)
    if acervo.responsavel != request.user:
        return redirect('acervo:acervo')
    if request.method == 'POST':
        form = AcervoForm(request.POST, request.FILES, instance=acervo)
        if form.is_valid():
            form.save()
            return redirect('acervo:detalhes_acervo', pk=pk)
    else:
        form = AcervoForm(instance=acervo)
    return render(request, 'acervo/submeter_acervo.html', {'form': form})

@login_required
def listar_acervo_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    acervo_items = Acervo.objects.filter(responsavel=usuario)

    paginator = Paginator(acervo_items, 10)
    page_number = request.GET.get('page')
    lista_acervos = paginator.get_page(page_number)

    context = {
        'acervo_items': lista_acervos,
        'form_filtro': AcervoForm(),
        'exibir_todos': False,
        'page_obj': lista_acervos,
    }

    return render(request, 'acervo/listar_acervo.html', context)
