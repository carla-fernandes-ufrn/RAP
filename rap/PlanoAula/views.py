from audioop import reverse
from django import forms
from django.contrib import messages 
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.http import HttpResponse 
import json
from django.http import JsonResponse
import datetime
import zipfile
import base64

from django.urls import reverse_lazy
from django.views import generic
from django_filters.views import BaseFilterView, FilterView
from Disciplina.models import Disciplina, Conteudo
from PlanoAula.models import PlanoAula, FotoRobo, VideoRobo, FotoExecucao, VideoExecucao, LikePlanoAula, ExecucaoPlanoAula
from Usuario.models import Usuario
from PlanoAula import forms, filters

@login_required
def home(request):

    if (not request.user.first_name or not request.user.last_name):
        return redirect('usuario:completar_cadastro', pk = request.user.pk)
    
    planos_aula = PlanoAula.objects.all()
    conteudos = list(Conteudo.objects.filter(status='Ativo'))
    disciplinas = list(Disciplina.objects.filter(status='Ativo'))

    inf_disciplinas = encontrar_planos_aula_disciplina(planos_aula, disciplinas)
    principais_conteudos = encontrar_principais_conteudos(likes_execucao_por_conteudo(planos_aula, conteudos), 5)
    principais_planos_aula = encontrar_principais_planos_aula(planos_aula, 6)

    # definir_principais_disciplinas(request.user.id)

    informacoes = {
        'lista_planos_aula': planos_aula[:10],
        'principais_conteudos': principais_conteudos,
        'principais_planos_aula': principais_planos_aula,
        'inf_disciplinas': inf_disciplinas
    }

    return render(request, "home.html", informacoes)

    # return render(request, "Base/home.html")

class Criar(generic.CreateView, LoginRequiredMixin):
    model = PlanoAula
    fields = ['titulo', 'contextualizacao', 'descricao_atividade', 'conteudos']
    template_name = 'PlanoAula/criar.html'
    success_url = reverse_lazy('plano_aula:listar')

    def form_valid(self, form):
        usuario = Usuario.objects.get(username=self.request.user.username)
        form.instance.responsavel = usuario
        return super().form_valid(form)

    # Cria no HTML um objeto "form"

@login_required
def criar(request):
    if (request.method == 'POST'):
        form_inf_gerais = forms.FormInfGerais(request.POST)
        form_montagem = forms.FormMontagem(request.POST)
        form_programacao = forms.FormProgramacao(request.POST, request.FILES)
        form_midias_robo_fotos = forms.FormMidiasRoboFotos(request.POST)
        robo_fotos = request.FILES.getlist('robo_foto')
        form_midias_robo_videos = forms.FormMidiasRoboVideos(request.POST)
        robo_videos = request.FILES.getlist('robo_video')
        form_midias_robo = forms.FormMidiasRobo(request.POST, request.FILES)
        form_midias_execucao_fotos = forms.FormMidiasExecucaoFotos(request.POST)
        execucao_fotos = request.FILES.getlist('execucao_foto')
        form_midias_execucao_videos = forms.FormMidiasExecucaoVideos(request.POST)
        execucao_videos = request.FILES.getlist('execucao_video')
        if (form_inf_gerais.is_valid() and form_montagem.is_valid() and form_programacao.is_valid()
                and form_midias_robo.is_valid() and form_midias_robo_fotos.is_valid() 
                and form_midias_robo_videos.is_valid() and form_midias_execucao_fotos.is_valid() 
                and form_midias_execucao_videos.is_valid()):

            conteudos = request.POST.get('lista_id_conteudos','').split(',')

            plano_aula = PlanoAula()
            plano_aula.criador = Usuario.objects.get(id=request.user.id)

            # Informações gerais
            plano_aula.titulo = form_inf_gerais.cleaned_data['titulo']
            plano_aula.contextualizacao = form_inf_gerais.cleaned_data['contextualizacao']
            plano_aula.descricao_atividade = form_inf_gerais.cleaned_data['descricao_atividade']
            if (form_inf_gerais.cleaned_data['avaliacao'] != ""):
                plano_aula.avaliacao = form_inf_gerais.cleaned_data['avaliacao']

            # Montagem
            if (form_montagem.cleaned_data['robo_equipamento'] != ""):
                plano_aula.robo_equipamento = form_montagem.cleaned_data['robo_equipamento']
            if (form_montagem.cleaned_data['robo_descricao'] != ""):
                plano_aula.robo_descricao = form_montagem.cleaned_data['robo_descricao']
            if (form_montagem.cleaned_data['robo_link'] != ""):
                plano_aula.robo_link = form_montagem.cleaned_data['robo_link']

            # Programação
            if (form_programacao.cleaned_data['prog_linguagem'] != ""):
                plano_aula.prog_linguagem = form_programacao.cleaned_data['prog_linguagem']
            if (form_programacao.cleaned_data['prog_descricao'] != ""):
                plano_aula.prog_descricao = form_programacao.cleaned_data['prog_descricao']
            if (form_programacao.cleaned_data['prog_link'] != ""):
                plano_aula.prog_link = form_programacao.cleaned_data['prog_link']
            if (form_programacao.cleaned_data['prog_codigos'] != ""):
                plano_aula.prog_codigos = form_programacao.cleaned_data['prog_codigos']

            if (form_midias_robo.cleaned_data['robo_pdf'] != ""):
                plano_aula.robo_pdf = form_midias_robo.cleaned_data['robo_pdf']
            
            plano_aula.save()

            # Midias robo
                
            if (robo_fotos != []):
                for foto in robo_fotos:
                    print(plano_aula)
                    print(foto)
                    FotoRobo(plano_aula=plano_aula, robo_foto=foto).save()
                
            if (robo_videos != []):
                for video in robo_videos:
                    VideoRobo(plano_aula=plano_aula, robo_video=video).save()

            # Midias execução
                
            if (execucao_fotos != []):
                for foto in execucao_fotos:
                    FotoExecucao(plano_aula=plano_aula, execucao_foto=foto).save()
                
            if (execucao_videos != []):
                for video in execucao_videos:
                    VideoExecucao(plano_aula=plano_aula, execucao_video=video).save()

            # Adicionar conteúdos
            if (conteudos != ['']):
                for conteudo in conteudos:
                    plano_aula.conteudos.add(Conteudo.objects.get(id=int(conteudo)))
            
            # Salvar
            plano_aula.save()

            return redirect('plano_aula:listar')
    else:
        form_inf_gerais = forms.FormInfGerais()
        form_montagem = forms.FormMontagem()
        form_programacao = forms.FormProgramacao()
        form_midias_robo_fotos = forms.FormMidiasRoboFotos()
        form_midias_robo_videos = forms.FormMidiasRoboVideos()
        form_midias_robo = forms.FormMidiasRobo()
        form_midias_execucao_fotos = forms.FormMidiasExecucaoFotos()
        form_midias_execucao_videos = forms.FormMidiasExecucaoVideos()
        lista_disciplinas = Disciplina.objects.filter(status="Ativo")
        lista_conteudos = Conteudo.objects.filter(status="Ativo")
        informacoes = {
            'form_inf_gerais': form_inf_gerais,
            'form_montagem': form_montagem,
            'form_programacao': form_programacao,
            'form_midias_robo_fotos': form_midias_robo_fotos,
            'form_midias_robo_videos': form_midias_robo_videos,
            'form_midias_robo': form_midias_robo,
            'form_midias_execucao_fotos': form_midias_execucao_fotos,
            'form_midias_execucao_videos': form_midias_execucao_videos,
            'lista_disciplinas': lista_disciplinas,
            'lista_conteudos': lista_conteudos,
        }

        return render(request, "PlanoAula/criar.html", informacoes)


@login_required
def listar(request):
    planos_aula = PlanoAula.objects.all()
    principais_conteudos = Conteudo.objects.filter(status='Ativos')
    disciplinas = list(Disciplina.objects.filter(status='Ativo'))

    inf_disciplinas = encontrar_planos_aula_disciplina(planos_aula, disciplinas)

    # encontrar_principais_conteudos(disciplinas)

    informacoes = {
        'lista_planos_aula': planos_aula[:10],
        'principais_conteudos': principais_conteudos,
        'inf_disciplinas': inf_disciplinas
    }

    return render(request, "PlanoAula/listar.html", informacoes)

@login_required
def listar_todos(request):
    planos_aula = PlanoAula.objects.all()

    informacoes = {
        'lista_planos_aula': planos_aula
    }

    return render(request, "PlanoAula/listar.html", informacoes)

class ListarPlanosAulaFiltrados(generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.all())
        qs_filtrada = planos_aula_filtrado.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(ListarPlanosAulaFiltrados,self).get_context_data(**kwargs)
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.all())
        context['planos_aula_filtrado'] = planos_aula_filtrado.qs
        context['form_filtro'] = planos_aula_filtrado.form
        context['tipo'] = "todos"
        return context

class ListarPlanosAulaFiltradosUsuario(generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(criador=usuario))
        qs_filtrada = planos_aula_filtrado.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(ListarPlanosAulaFiltradosUsuario,self).get_context_data(**kwargs)
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(criador=usuario))
        context['planos_aula_filtrado'] = planos_aula_filtrado.qs
        context['form_filtro'] = planos_aula_filtrado.form
        context['tipo'] = "usuario"
        return context

class ListarPlanosAulaFiltradosFavoritos(generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        id_planos_aula_favoritos = list(LikePlanoAula.objects.filter(usuario=usuario).values_list('plano_aula', flat=True))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(id__in = id_planos_aula_favoritos))
        qs_filtrada = planos_aula_filtrado.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(ListarPlanosAulaFiltradosFavoritos,self).get_context_data(**kwargs)
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        id_planos_aula_favoritos = list(LikePlanoAula.objects.filter(usuario=usuario).values_list('plano_aula', flat=True))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(id__in = id_planos_aula_favoritos))
        context['planos_aula_filtrado'] = planos_aula_filtrado.qs
        context['form_filtro'] = planos_aula_filtrado.form
        context['tipo'] = "favoritos"
        return context

class ListarPlanosAulaFiltradosExecutados(generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        id_planos_aula_executados = list(ExecucaoPlanoAula.objects.filter(usuario=usuario).values_list('plano_aula', flat=True))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(id__in = id_planos_aula_executados))
        qs_filtrada = planos_aula_filtrado.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(ListarPlanosAulaFiltradosExecutados,self).get_context_data(**kwargs)
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        id_planos_aula_executados = list(ExecucaoPlanoAula.objects.filter(usuario=usuario).values_list('plano_aula', flat=True))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(id__in = id_planos_aula_executados))
        context['planos_aula_filtrado'] = planos_aula_filtrado.qs
        context['form_filtro'] = planos_aula_filtrado.form
        context['tipo'] = "executados"
        return context

@login_required
def espaco_usuario(request):
    planos_aula_usuario = PlanoAula.objects.filter(criador=request.user)
    id_planos_aula_favoritados = list(LikePlanoAula.objects.filter(usuario=request.user).values_list('plano_aula', flat=True))
    planos_aula_favoritados = PlanoAula.objects.filter(id__in = id_planos_aula_favoritados)
    id_planos_aula_executados = list(ExecucaoPlanoAula.objects.filter(usuario=request.user).values_list('plano_aula', flat=True))
    planos_aula_executados = PlanoAula.objects.filter(id__in = id_planos_aula_executados)

    informacoes = {
        'planos_aula_usuario': planos_aula_usuario,
        'planos_aula_favoritados': planos_aula_favoritados,
        'planos_aula_executados': planos_aula_executados
    }

    return render(request, 'PlanoAula/espaco_usuario.html', informacoes)

class EspacoUsuario(generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/espaco_usuario.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(criador=self.request.user))
        qs_filtrada = planos_aula_filtrado.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(EspacoUsuario,self).get_context_data(**kwargs)
        meus_planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(criador=self.request.user))
        planos_aula_favoritados_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.all())
        context['meus_planos_aula_filtrado'] = meus_planos_aula_filtrado.qs
        context['form_meus_planos_aula_filtro'] = meus_planos_aula_filtrado.form
        return context

class ListarPlanosAula(FilterView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 3
    filterset_class = filters.PlanoAulaFiltro

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

@login_required
def listar_usuario(request, pk):
    lista_aulas = PlanoAula.objects.filter(responsavel__pk=pk)

    informacoes = {
        'lista_aulas': lista_aulas
    }

    return render(request, "PlanoAula/listar.html", informacoes)


class Editar(generic.UpdateView):
    model = PlanoAula
    form_class = forms.FormEditarPlano_aula
    template_name = 'PlanoAula/editar.html'
    success_url = reverse_lazy('plano_aula:listar')
    fieelds = ["titulo", "contextualizacao", "descricao_atividade"]

class Detalhe(generic.DetailView):
   model = PlanoAula
   template_name = "PlanoAula/detalhes.html"
   context_object_name = "plano_aula"

   def get_context_data(self,**kwargs):
        context = super(Detalhe,self).get_context_data(**kwargs)
        robo_fotos = FotoRobo.objects.filter(plano_aula = self.get_object().pk)
        context['robo_fotos'] = robo_fotos
        robo_videos = VideoRobo.objects.filter(plano_aula = self.get_object().pk)
        context['robo_videos'] = robo_videos
        execucao_fotos = FotoExecucao.objects.filter(plano_aula = self.get_object().pk)
        context['execucao_fotos'] = execucao_fotos
        execucao_videos = VideoExecucao.objects.filter(plano_aula = self.get_object().pk)
        context['execucao_videos'] = execucao_videos
        return context

class Deletar(generic.DeleteView):
    model = PlanoAula
    template_name = 'PlanoAula/deletar.html'
    success_url = reverse_lazy('plano_aula:listar')

class Programacao(generic.DetailView):
   model = PlanoAula
   template_name = "PlanoAula/programacao.html"
   context_object_name = "plano_aula"

def marcar_favorito(request, plano_aula, usuario):
    plano_aula_obj = PlanoAula.objects.get(id=plano_aula)
    usuario_obj = Usuario.objects.get(id=usuario)
    like = LikePlanoAula.objects.filter(plano_aula__id = plano_aula, usuario__id = usuario)
    if len(like) == 0:
        LikePlanoAula.objects.create(plano_aula = plano_aula_obj, usuario = usuario_obj)
        return finalizar_requisicao_api(1)
    else:
        like[0].delete()
        return finalizar_requisicao_api(0)


def marcar_executado(request, plano_aula, usuario):
    plano_aula_obj = PlanoAula.objects.get(id=plano_aula)
    usuario_obj = Usuario.objects.get(id=usuario)
    execucao = ExecucaoPlanoAula.objects.filter(plano_aula__id = plano_aula, usuario__id = usuario)
    if len(execucao) == 0:
        ExecucaoPlanoAula.objects.create(plano_aula = plano_aula_obj, usuario = usuario_obj)
        return finalizar_requisicao_api(1)
    else:
        execucao[0].delete()
        return finalizar_requisicao_api(0)

def finalizar_requisicao_api(response_data):
    response_data = response_data

    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )