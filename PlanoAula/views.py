from django.urls import reverse
from django import forms
from django.contrib import messages 
from django.core import serializers
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from django.http import HttpResponse, HttpResponseRedirect

from django.core.exceptions import PermissionDenied
import json
from django.http import JsonResponse
import datetime
import zipfile
import base64

from django.urls import reverse_lazy
from django.views import generic
from django_filters.views import BaseFilterView, FilterView
from Disciplina.models import Disciplina, Conteudo
from PlanoAula.models import PlanoAula, FotoRobo, VideoRobo, FotoExecucao, VideoExecucao, LikePlanoAula, ExecucaoPlanoAula, MensagemPlanoAula
from Usuario.models import Usuario
from PlanoAula import forms, filters

@login_required
def criar(request):
    lista_disciplinas = Disciplina.objects.filter(status="Ativo")
    lista_conteudos = Conteudo.objects.filter(status="Ativo")

    if (request.method == 'POST'):
        form_inf_gerais = forms.FormInfGerais(request.POST)
        form_montagem = forms.FormMontagem(request.POST, request.FILES)
        form_programacao = forms.FormProgramacao(request.POST, request.FILES)

        conteudos = request.POST.get('lista_id_conteudos','').split(',')
        conteudos_ids = [int(id) for id in conteudos if id.isdigit()]
        conteudos_selecionados = Conteudo.objects.filter(id__in=conteudos_ids)

        if (form_inf_gerais.is_valid() and form_montagem.is_valid() and form_programacao.is_valid()):

            plano_aula = PlanoAula()
            plano_aula.criador = Usuario.objects.get(id=request.user.id)

            # Informações gerais
            plano_aula.titulo = form_inf_gerais.cleaned_data['titulo']
            plano_aula.contextualizacao = form_inf_gerais.cleaned_data['contextualizacao']
            plano_aula.descricao_atividade = form_inf_gerais.cleaned_data['descricao_atividade']
            if (form_inf_gerais.cleaned_data['avaliacao'] != ""):
                plano_aula.avaliacao = form_inf_gerais.cleaned_data['avaliacao']

            # Montagem
            if (form_montagem.cleaned_data['nivel_dificuldade_montagem'] != ""):
                plano_aula.nivel_dificuldade_montagem = form_montagem.cleaned_data['nivel_dificuldade_montagem']
            if (form_montagem.cleaned_data['robo_equipamento'] != ""):
                plano_aula.robo_equipamento = form_montagem.cleaned_data['robo_equipamento']
            if (form_montagem.cleaned_data['robo_descricao'] != ""):
                plano_aula.robo_descricao = form_montagem.cleaned_data['robo_descricao']
            if (form_montagem.cleaned_data['robo_link'] != ""):
                plano_aula.robo_link = form_montagem.cleaned_data['robo_link']
            if (form_montagem.cleaned_data['robo_pdf'] != ""):
                plano_aula.robo_pdf = form_montagem.cleaned_data['robo_pdf']

            # Programação
            if (form_programacao.cleaned_data['nivel_dificuldade_programacao'] != ""):
                plano_aula.nivel_dificuldade_programacao = form_programacao.cleaned_data['nivel_dificuldade_programacao']
            if (form_programacao.cleaned_data['prog_linguagem'] != ""):
                plano_aula.prog_linguagem = form_programacao.cleaned_data['prog_linguagem']
            if (form_programacao.cleaned_data['prog_descricao'] != ""):
                plano_aula.prog_descricao = form_programacao.cleaned_data['prog_descricao']
            if (form_programacao.cleaned_data['prog_link'] != ""):
                plano_aula.prog_link = form_programacao.cleaned_data['prog_link']
            if (form_programacao.cleaned_data['prog_codigos'] != ""):
                plano_aula.prog_codigos = form_programacao.cleaned_data['prog_codigos']
            
            plano_aula.save()

            # Adicionar conteúdos
            if (conteudos != ['']):
                for conteudo in conteudos:
                    plano_aula.conteudos.add(Conteudo.objects.get(id=int(conteudo)))
            
            # Salvar
            plano_aula.save()

            return redirect('plano_aula:detalhes', pk=plano_aula.pk)

        if not form_inf_gerais.is_valid():
            aba = 'inf_gerais'
        else:
            aba = 'montagem_programacao'

        informacoes = {
            'form_inf_gerais': form_inf_gerais,
            'form_montagem': form_montagem,
            'form_programacao': form_programacao,
            'lista_disciplinas': lista_disciplinas,
            'lista_conteudos': lista_conteudos,
            'conteudos_selecionados': conteudos_selecionados,
            'lista_id_conteudos': ','.join(str(id) for id in conteudos_ids),
            'aba': aba
        }
        return render(request, "PlanoAula/criar.html", informacoes)
    else:
        form_inf_gerais = forms.FormInfGerais()
        form_montagem = forms.FormMontagem()
        form_programacao = forms.FormProgramacao()
        informacoes = {
            'form_inf_gerais': form_inf_gerais,
            'form_montagem': form_montagem,
            'form_programacao': form_programacao,
            'lista_disciplinas': lista_disciplinas,
            'lista_conteudos': lista_conteudos,
        }

        return render(request, "PlanoAula/criar.html", informacoes)

class Detalhe(LoginRequiredMixin, FormMixin, generic.DetailView):
    model = PlanoAula
    template_name = "PlanoAula/detalhes.html"
    context_object_name = "plano_aula"
    form_class = forms.FormNovaMensagem

    def get_success_url(self):
        return reverse('plano_aula:detalhes', kwargs={'pk': self.object.id}) + '?aba=comentarios'

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

        lista_mensagens = MensagemPlanoAula.objects.filter(plano_aula__id = self.kwargs['pk'], mensagem_original = None)
        context['lista_mensagens'] = lista_mensagens
        context['form_nome_mensagem'] = forms.FormNovaMensagem()
        return context
   
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        usuario = Usuario.objects.get(pk=self.request.user.pk)
        plano_aula = PlanoAula.objects.get(pk=self.object.id)

        form.instance.usuario = usuario
        form.instance.plano_aula = plano_aula
        if (self.request.POST.get('mensagem_original') != ""):
            mensagem_original = MensagemPlanoAula.objects.get(pk=self.request.POST.get('mensagem_original'))
            form.instance.mensagem_original = mensagem_original

        form.save()
        return super(Detalhe, self).form_valid(form)

@login_required
def editar_midia(request, pk):

    plano_aula = PlanoAula.objects.get(id=pk)
    if (request.user.id == plano_aula.criador.id):
        if (request.method == 'POST'):
            if ('submit-form_robo_foto' in request.POST):
                form = forms.FormMidiasRoboFotos(request.POST, request.FILES)
                if form.is_valid():
                    FotoRobo.objects.create(plano_aula=plano_aula, robo_foto=form.cleaned_data.get('robo_foto'))
            if ('submit-form_robo_video' in request.POST):
                form = forms.FormMidiasRoboVideos(request.POST, request.FILES)
                if form.is_valid():
                    VideoRobo.objects.create(plano_aula=plano_aula, robo_video=form.cleaned_data.get('robo_video'))
            if ('submit-form_execucao_foto' in request.POST):
                form = forms.FormMidiasExecucaoFotos(request.POST, request.FILES)
                if form.is_valid():
                    FotoExecucao.objects.create(plano_aula=plano_aula, execucao_foto=form.cleaned_data.get('execucao_foto'))
            if ('submit-form_execucao_video' in request.POST):
                form = forms.FormMidiasExecucaoVideos(request.POST, request.FILES)
                if form.is_valid():
                    VideoExecucao.objects.create(plano_aula=plano_aula, execucao_video=form.cleaned_data.get('execucao_video'))

        robo_fotos = plano_aula.fotos_robo
        robo_videos = plano_aula.videos_robo
        execucao_fotos = plano_aula.fotos_execucao
        execucao_videos = plano_aula.videos_execucao

        informacoes =  {
            'plano_aula': plano_aula,
            'robo_fotos': robo_fotos,
            'robo_videos': robo_videos,
            'execucao_fotos': execucao_fotos,
            'execucao_videos': execucao_videos,
            'form_robo_fotos': forms.FormMidiasRoboFotos(),
            'form_robo_videos': forms.FormMidiasRoboVideos(),
            'form_execucao_fotos': forms.FormMidiasExecucaoFotos(),
            'form_execucao_videos': forms.FormMidiasExecucaoVideos(),
        }

        return render(request, "PlanoAula/editar_midias.html", informacoes)
    else:
        raise PermissionDenied()

@login_required
def deletar_midia(request,tipo, pk):
    if (tipo == 1):
        objeto_deletado = FotoRobo.objects.get(pk=pk)
    elif (tipo == 2):
        objeto_deletado = VideoRobo.objects.get(pk=pk)
    elif (tipo == 3):
        objeto_deletado = FotoExecucao.objects.get(pk=pk)
    elif (tipo == 4):
        objeto_deletado = VideoExecucao.objects.get(pk=pk)
    plano_aula = objeto_deletado.plano_aula
    if (request.user.id == plano_aula.criador.id):
        objeto_deletado.delete()
        return redirect('plano_aula:editar_midia', pk=plano_aula.pk)
    else:
        raise PermissionDenied()

@login_required
def editar(request, pk):
    plano_aula = PlanoAula.objects.get(pk=pk)
    if (plano_aula.criador.pk == request.user.pk):
        if (request.method == 'POST'):
            form_inf_gerais = forms.FormInfGerais(request.POST)
            form_montagem = forms.FormMontagem(request.POST, request.FILES)
            form_programacao = forms.FormProgramacao(request.POST, request.FILES)
            if (form_inf_gerais.is_valid() and form_montagem.is_valid() and form_programacao.is_valid()):

                conteudos = request.POST.get('lista_id_conteudos','').split(',')

                # Informações gerais
                plano_aula.titulo = form_inf_gerais.cleaned_data['titulo']
                plano_aula.contextualizacao = form_inf_gerais.cleaned_data['contextualizacao']
                plano_aula.descricao_atividade = form_inf_gerais.cleaned_data['descricao_atividade']
                if (form_inf_gerais.cleaned_data['avaliacao'] != ""):
                    plano_aula.avaliacao = form_inf_gerais.cleaned_data['avaliacao']

                # Montagem
                if (form_montagem.cleaned_data['nivel_dificuldade_montagem'] != ""):
                    plano_aula.nivel_dificuldade_montagem = form_montagem.cleaned_data['nivel_dificuldade_montagem']
                if (form_montagem.cleaned_data['robo_equipamento'] != ""):
                    plano_aula.robo_equipamento = form_montagem.cleaned_data['robo_equipamento']
                if (form_montagem.cleaned_data['robo_descricao'] != ""):
                    plano_aula.robo_descricao = form_montagem.cleaned_data['robo_descricao']
                if (form_montagem.cleaned_data['robo_link'] != ""):
                    plano_aula.robo_link = form_montagem.cleaned_data['robo_link']
                if (form_montagem.cleaned_data['robo_pdf'] != ""):
                    plano_aula.robo_pdf = form_montagem.cleaned_data['robo_pdf']

                # Programação
                if (form_programacao.cleaned_data['nivel_dificuldade_programacao'] != ""):
                    plano_aula.nivel_dificuldade_programacao = form_programacao.cleaned_data['nivel_dificuldade_programacao']
                if (form_programacao.cleaned_data['prog_linguagem'] != ""):
                    plano_aula.prog_linguagem = form_programacao.cleaned_data['prog_linguagem']
                if (form_programacao.cleaned_data['prog_descricao'] != ""):
                    plano_aula.prog_descricao = form_programacao.cleaned_data['prog_descricao']
                if (form_programacao.cleaned_data['prog_link'] != ""):
                    plano_aula.prog_link = form_programacao.cleaned_data['prog_link']
                if (form_programacao.cleaned_data['prog_codigos'] != ""):
                    plano_aula.prog_codigos = form_programacao.cleaned_data['prog_codigos']
                
                plano_aula.save()

                # Adicionar conteúdos

                conteudos_plano_aula = list(plano_aula.conteudos.all().values_list('pk', flat=True))

                if(conteudos != ['']):
                    for conteudo in conteudos:
                        if (int(conteudo) not in conteudos_plano_aula):
                            plano_aula.conteudos.add(Conteudo.objects.get(id=int(conteudo)))
                    for conteudo in conteudos_plano_aula:
                        if (str(conteudo) not in conteudos):
                            plano_aula.conteudos.remove(Conteudo.objects.get(id=int(conteudo)))
                else:
                    for conteudo in plano_aula.conteudos.all():
                        plano_aula.conteudos.remove(conteudo)
                    
                # Salvar
                plano_aula.save()

                return redirect('plano_aula:detalhes', pk=pk)
        else:
            form_inf_gerais = forms.FormInfGerais(instance=plano_aula)
            form_montagem = forms.FormMontagem(instance=plano_aula)
            form_programacao = forms.FormProgramacao(instance=plano_aula)

            lista_disciplinas = Disciplina.objects.filter(status="Ativo")
            lista_conteudos = Conteudo.objects.filter(status="Ativo")

            print(list(plano_aula.conteudos.all()))

            informacoes = {
                'form_inf_gerais': form_inf_gerais,
                'form_montagem': form_montagem,
                'form_programacao': form_programacao,
                'lista_disciplinas': lista_disciplinas,
                'lista_conteudos': lista_conteudos,
                'conteudos_plano_aula': serializers.serialize("json", plano_aula.conteudos.all()),
                'plano_aula': plano_aula,
            }

            return render(request, "PlanoAula/editar.html", informacoes)
    else:
        raise PermissionDenied()

@login_required
def deletar_mensagem(request, pk):
    mensagem = MensagemPlanoAula.objects.get(id=pk)
    if (request.user.id == mensagem.usuario.id or 
        request.user.id == mensagem.plano_aula.criador.id or
        request.user.is_superuser or
        (mensagem.mensagem_original is not None and request.user.id == mensagem.mensagem_original.usuario.id)):
        plano_aula_id = mensagem.plano_aula.id
        mensagem.delete()

        return HttpResponseRedirect(reverse('plano_aula:detalhes', kwargs={'pk': plano_aula_id}) + '?aba=comentarios')
    else:
        raise PermissionDenied()

@login_required
def desabilitar(request, pk):
    plano_aula = PlanoAula.objects.get(pk=pk)
    if (plano_aula.criador.pk == request.user.pk):
        plano_aula.status = False
        plano_aula.save()
        return redirect('plano_aula:listar')
    else:
        raise PermissionDenied()
    
class Deletar(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = PlanoAula
    template_name = 'PlanoAula/deletar.html'
    success_url = reverse_lazy('plano_aula:listar')

    def test_func(self):
        plano_aula = PlanoAula.objects.get(pk=int(self.kwargs['pk']))
        return self.request.user.id == plano_aula.criador.id

@login_required
def listar(request):
    planos_aula = PlanoAula.objects.filter(status=True)
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
    planos_aula = PlanoAula.objects.filter(status=True)

    informacoes = {
        'lista_planos_aula': planos_aula
    }

    return render(request, "PlanoAula/listar.html", informacoes)

class ListarPlanosAulaFiltrados(LoginRequiredMixin, generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(status=True))
        qs_filtrada = planos_aula_filtrado.qs.distinct()
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(ListarPlanosAulaFiltrados,self).get_context_data(**kwargs)
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(status=True))
        context['planos_aula_filtrado'] = planos_aula_filtrado.qs
        context['form_filtro'] = planos_aula_filtrado.form
        context['tipo'] = "todos"
        return context

class ListarPlanosAulaFiltradosUsuario(LoginRequiredMixin, generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(status=True, criador=usuario))
        qs_filtrada = planos_aula_filtrado.qs.distinct()
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(ListarPlanosAulaFiltradosUsuario,self).get_context_data(**kwargs)
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(status=True, criador=usuario))
        context['planos_aula_filtrado'] = planos_aula_filtrado.qs
        context['form_filtro'] = planos_aula_filtrado.form
        context['tipo'] = "usuario"
        return context

class ListarPlanosAulaFiltradosFavoritos(LoginRequiredMixin, generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        id_planos_aula_favoritos = list(LikePlanoAula.objects.filter(usuario=usuario).values_list('plano_aula', flat=True))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(id__in = id_planos_aula_favoritos, status=True))
        qs_filtrada = planos_aula_filtrado.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(ListarPlanosAulaFiltradosFavoritos,self).get_context_data(**kwargs)
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        id_planos_aula_favoritos = list(LikePlanoAula.objects.filter(usuario=usuario).values_list('plano_aula', flat=True))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(id__in = id_planos_aula_favoritos, status=True))
        context['planos_aula_filtrado'] = planos_aula_filtrado.qs
        context['form_filtro'] = planos_aula_filtrado.form
        context['tipo'] = "favoritos"
        return context

class ListarPlanosAulaFiltradosExecutados(LoginRequiredMixin, generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        id_planos_aula_executados = list(ExecucaoPlanoAula.objects.filter(usuario=usuario).values_list('plano_aula', flat=True))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(id__in = id_planos_aula_executados, status=True))
        qs_filtrada = planos_aula_filtrado.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(ListarPlanosAulaFiltradosExecutados,self).get_context_data(**kwargs)
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        id_planos_aula_executados = list(ExecucaoPlanoAula.objects.filter(usuario=usuario).values_list('plano_aula', flat=True))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(id__in = id_planos_aula_executados, status=True))
        context['planos_aula_filtrado'] = planos_aula_filtrado.qs
        context['form_filtro'] = planos_aula_filtrado.form
        context['tipo'] = "executados"
        return context

@login_required
def espaco_usuario(request):
    planos_aula_usuario = PlanoAula.objects.filter(criador=request.user, status=True)
    id_planos_aula_favoritados = list(LikePlanoAula.objects.filter(usuario=request.user).values_list('plano_aula', flat=True))
    planos_aula_favoritados = PlanoAula.objects.filter(id__in = id_planos_aula_favoritados, status=True)
    id_planos_aula_executados = list(ExecucaoPlanoAula.objects.filter(usuario=request.user).values_list('plano_aula', flat=True))
    planos_aula_executados = PlanoAula.objects.filter(id__in = id_planos_aula_executados, status=True)

    informacoes = {
        'planos_aula_usuario': planos_aula_usuario,
        'planos_aula_favoritados': planos_aula_favoritados,
        'planos_aula_executados': planos_aula_executados
    }

    return render(request, 'PlanoAula/espaco_usuario.html', informacoes)

class EspacoUsuario(LoginRequiredMixin, generic.ListView):
    model = PlanoAula
    template_name = 'PlanoAula/espaco_usuario.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(criador=self.request.user, status=True))
        qs_filtrada = planos_aula_filtrado.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(EspacoUsuario,self).get_context_data(**kwargs)
        meus_planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(criador=self.request.user, status=True))
        planos_aula_favoritados_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(status=True))
        context['meus_planos_aula_filtrado'] = meus_planos_aula_filtrado.qs
        context['form_meus_planos_aula_filtro'] = meus_planos_aula_filtrado.form
        return context

class ListarPlanosAula(LoginRequiredMixin, FilterView):
    model = PlanoAula
    template_name = 'PlanoAula/listar.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 3
    filterset_class = filters.PlanoAulaFiltro

@login_required
def listar_usuario(request, pk):
    lista_aulas = PlanoAula.objects.filter(responsavel__pk=pk, status=True)

    informacoes = {
        'lista_aulas': lista_aulas
    }

    return render(request, "PlanoAula/listar.html", informacoes)



@login_required
def marcar_favorito(request, plano_aula, usuario):
    if (request.user.pk == usuario):
        plano_aula_obj = PlanoAula.objects.get(id=plano_aula)
        usuario_obj = Usuario.objects.get(id=usuario)
        like = LikePlanoAula.objects.filter(plano_aula__id = plano_aula, usuario__id = usuario)
        if len(like) == 0:
            LikePlanoAula.objects.create(plano_aula = plano_aula_obj, usuario = usuario_obj)
            return HttpResponse(
                json.dumps(1),
                content_type="application/json"
            )
        else:
            like[0].delete()
            return HttpResponse(
                json.dumps(0),
                content_type="application/json"
            )
    else:
        raise PermissionDenied()

@login_required
def marcar_executado(request, plano_aula, usuario):
    if (request.user.pk == usuario):
        plano_aula_obj = PlanoAula.objects.get(id=plano_aula)
        usuario_obj = Usuario.objects.get(id=usuario)
        execucao = ExecucaoPlanoAula.objects.filter(plano_aula__id = plano_aula, usuario__id = usuario)
        if len(execucao) == 0:
            ExecucaoPlanoAula.objects.create(plano_aula = plano_aula_obj, usuario = usuario_obj)
            return HttpResponse(
                json.dumps(1),
                content_type="application/json"
            )
        else:
            execucao[0].delete()
            return HttpResponse(
                json.dumps(0),
                content_type="application/json"
            )
    else:
        raise PermissionDenied()

@login_required
def finalizar_requisicao_api(response_data):
    response_data = response_data

    return HttpResponse(
        json.dumps(response_data),
        content_type="application/json"
    )