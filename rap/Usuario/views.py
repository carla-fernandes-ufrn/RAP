from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views import generic

from django.http import JsonResponse
from django.core import serializers

from Usuario import forms
from Usuario.models import Usuario, Interesses
from Disciplina.models import Disciplina
from PlanoAula.models import PlanoAula
from PlanoAula import filters as filter_plano_aula
from Acoes.models import Acoes
from Acoes import filters as filter_acoes

@login_required
def listar_ativos(request):
    lista_usuarios = Usuario.objects.filter(is_active=True)
    
    informacoes = {
        'lista_usuarios': lista_usuarios,
        'ativos': True
    }

    return render(request, "Usuario/listar.html", informacoes)

@login_required
def listar_inativos(request):
    lista_usuarios = Usuario.objects.filter(is_active=False)
    
    informacoes = {
        'lista_usuarios': lista_usuarios,
        'ativos': False
    }

    return render(request, "Usuario/listar.html", informacoes)

@login_required
def mudar_status(request, pk):
    usuario = Usuario.objects.get(pk=pk)
    usuario.is_active = not usuario.is_active
    usuario.save()

    return redirect('usuario:listar_ativos')

@login_required
def mudar_status_admin(request, pk):
    usuario = Usuario.objects.get(pk=pk)
    usuario.is_superuser = not usuario.is_superuser
    usuario.save()
    
    return redirect('usuario:listar_ativos')

class Cadastrar(generic.CreateView):
    form_class = forms.FormCriarUsuario
    template_name = 'Usuario/cadastrar.html'
    success_url = reverse_lazy('usuario:login')

@login_required
def completar_cadastro(request):

    disciplinas = Disciplina.objects.filter(status='Ativo')

    interesses = list(Interesses.objects.filter(usuario = Usuario.objects.get(id =request.user.pk)).values_list('disciplina', flat=True))

    if (request.method == "POST"):
        form_usuario = forms.FormCompletarCadastro(request.POST)
        if (form_usuario.is_valid()):
            usuario = Usuario.objects.get(pk=request.user.pk)
            usuario.first_name = form_usuario.cleaned_data['first_name']
            usuario.last_name = form_usuario.cleaned_data['last_name']
            usuario.cidade = form_usuario.cleaned_data['cidade']
            usuario.estado = form_usuario.cleaned_data['estado']
            usuario.save()

            interesses_novos = request.POST.get('lista_interesses','').split(',')
            interesses_anteriores = list(Interesses.objects.filter(usuario = Usuario.objects.get(id =request.user.pk)).values_list('disciplina', flat=True))
            for interesse in interesses_novos:
                if int(interesse) not in interesses_anteriores:
                    disciplina = Disciplina.objects.get(id = int(interesse))
                    usuario.interesses.add(disciplina)
            for interesse in interesses_anteriores:
                if str(interesse) not in interesses_novos:
                    disciplina = Disciplina.objects.get(pk=interesse)
                    Interesses.objects.get(usuario=usuario, disciplina=disciplina).delete()
            return redirect('home')
        
    else:
        form_usuario = forms.FormCompletarCadastro()
        form_interesses = forms.FormAtualizarInteresses()
    
        informacoes = {
            'form_usuario': form_usuario,
            'form_interesses': form_interesses,
            'disciplinas': disciplinas,
            'interesses': interesses
        }
        return render(request, "usuario/completar_cadastro.html", informacoes)

class CompletarCadastro(LoginRequiredMixin, generic.UpdateView):
    model = Usuario
    form_class = forms.FormCompletarCadastro
    template_name = 'Usuario/completar_cadastro.html'
    success_url = reverse_lazy('home')

class Editar(LoginRequiredMixin, generic.UpdateView):
    model = Usuario
    form_class = forms.FormEditarUsuario
    template_name = 'Usuario/editar.html'

    def get_success_url(self):
           pk = self.kwargs["pk"]
           return reverse_lazy("usuario:editar", kwargs={"pk": pk})

@login_required
def alterar_avatar(request, pk, novo):
    if (novo == 0):
        usuario = Usuario.objects.get(pk=pk)
        usuario.avatar = 'profile-pic/default.jpeg'
        usuario.save()
        return redirect('usuario:editar', pk=pk)
    else:
        pass

class AlterarSenha(LoginRequiredMixin, generic.UpdateView):
    model = Usuario
    form_class = forms.FormEditarSenha
    template_name = 'Usuario/alterar_senha.html'

    def get_success_url(self):
           pk = self.kwargs["pk"]
           return reverse_lazy("usuario:editar", kwargs={"pk": pk})

class Detalhes(LoginRequiredMixin, generic.DetailView):
    model = Usuario
    template_name = "Usuario/detalhes.html"
    # usuario
    # object

class DeletarUser(LoginRequiredMixin, generic.DeleteView):
     model = Usuario
     template_name = 'Usuario/deletar.html'
     success_url = reverse_lazy('usuario:listar_ativos')

@login_required
def ler_informacoes_plano_aula(request, pk):
    usuario = Usuario.objects.get(pk=pk)

    planos_aula_filtrado = filter_plano_aula.PlanoAulaFiltro(request.GET, queryset=PlanoAula.objects.filter(criador=usuario))

    lista_planos_aula = planos_aula_filtrado.qs
    form_filtro_plano_aula = planos_aula_filtrado.form

    paginator_plano_aula = Paginator(lista_planos_aula, 10)

    page_number_plano_aula = request.GET.get("page")

    try:
        page_obj_plano_aula = paginator_plano_aula.page(page_number_plano_aula)
    except PageNotAnInteger:
        page_obj_plano_aula = paginator_plano_aula.page(1)
    except EmptyPage:
        page_obj_plano_aula = paginator_plano_aula.page(paginator_plano_aula.num_pages)

    informacoes = {
        'usuario': usuario,
        'form_filtro_plano_aula': form_filtro_plano_aula,
        'page_obj_plano_aula': page_obj_plano_aula,
    }

    return render(request, "Usuario/informacoes_plano_aula.html", informacoes)

@login_required
def ler_informacoes_acoes(request, pk):
    usuario = Usuario.objects.get(pk=pk)

    acoes_filtrado = filter_acoes.AcoesFiltro(request.GET, queryset=Acoes.objects.filter(responsavel=usuario))

    lista_acoes = acoes_filtrado.qs
    form_filtro_acoes = acoes_filtrado.form

    paginator_acoes = Paginator(lista_acoes, 10)

    page_number_acoes = request.GET.get("page")

    try:
        page_obj_acoes = paginator_acoes.page(page_number_acoes)
    except PageNotAnInteger:
        page_obj_acoes = paginator_acoes.page(1)
    except EmptyPage:
        page_obj_acoes = paginator_acoes.page(paginator_acoes.num_pages)

    informacoes = {
        'usuario': usuario,
        'form_filtro_acoes': form_filtro_acoes,
        'page_obj_acoes': page_obj_acoes,
    }

    return render(request, "Usuario/informacoes_acoes.html", informacoes)

class LerInformacoesUsuario(LoginRequiredMixin, generic.ListView):
    model = PlanoAula
    template_name = 'Usuario/informacoes.html'
    context_object_name = 'lista_planos_aula'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(criador=usuario))
        qs_filtrada = planos_aula_filtrado.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(LerInformacoesUsuario,self).get_context_data(**kwargs)
        usuario = Usuario.objects.get(pk=self.kwargs.get('pk'))
        planos_aula_filtrado = filters.PlanoAulaFiltro(self.request.GET, queryset=PlanoAula.objects.filter(criador=usuario))
        context['planos_aula_filtrado'] = planos_aula_filtrado.qs
        context['form_filtro'] = planos_aula_filtrado.form
        context['usuario'] = usuario
        return context

