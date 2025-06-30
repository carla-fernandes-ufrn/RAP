from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

from django.views import generic
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from django.http import JsonResponse
from django.core import serializers

from Usuario import forms
from Usuario import filters as filter_usuarios
from Usuario.models import Usuario, Interesses
from Disciplina.models import Disciplina
from PlanoAula.models import PlanoAula
from PlanoAula import filters as filter_plano_aula
from Acoes.models import Acoes
from Acoes import filters as filter_acoes

class ListarAtivos(LoginRequiredMixin, generic.ListView):
    model = Usuario
    template_name = 'Usuario/listar.html'
    context_object_name = 'lista_usuarios'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()
        usuarios_filtrados = filter_usuarios.UsuarioFiltro(self.request.GET, queryset=Usuario.objects.filter(is_active=True))
        qs_filtrada = usuarios_filtrados.qs
        return qs_filtrada

    def get_context_data(self,**kwargs):
        context = super(ListarAtivos,self).get_context_data(**kwargs)
        usuarios_filtrados = filter_usuarios.UsuarioFiltro(self.request.GET, queryset=Usuario.objects.filter(is_active=True))
        context['usuarios_filtrados'] = usuarios_filtrados.qs
        context['form_filtro'] = usuarios_filtrados.form
        context['exibir_todos'] = True
        return context

@login_required
def listar_ativos(request):

    usuarios_filtrado = filter_usuarios.UsuarioFiltro(request.GET, queryset=Usuario.objects.filter(is_active=True))

    print(Usuario.objects.filter(is_active=True))

    lista_usuarios = usuarios_filtrado.qs
    form_filtro_usuario = usuarios_filtrado.form

    paginator_usuario = Paginator(lista_usuarios, 10)

    page_number_usuario = request.GET.get("page")

    try:
        page_obj_usuario = paginator_usuario.page(page_number_usuario)
    except PageNotAnInteger:
        page_obj_usuario = paginator_usuario.page(1)
    except EmptyPage:
        page_obj_usuario = paginator_usuario.page(paginator_usuario.num_pages)

    informacoes = {
        'form_filtro_usuario': form_filtro_usuario,
        'page_obj_usuario': page_obj_usuario,
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

            if (interesses_novos != ['']):
                for interesse in interesses_novos:
                    if int(interesse) not in interesses_anteriores:
                        disciplina = Disciplina.objects.get(id = int(interesse))
                        usuario.interesses.add(disciplina)
            if (interesses_anteriores != []):
                for interesse in interesses_anteriores:
                    if str(interesse) not in interesses_novos:
                        disciplina = Disciplina.objects.get(pk=interesse)
                        Interesses.objects.get(usuario=usuario, disciplina=disciplina).delete()
            return redirect('home')
        else:
            informacoes = {
                'form_usuario': form_usuario,
                'form_interesses': form_interesses,
                'disciplinas': disciplinas,
                'interesses': interesses
            }
            return render(request, "usuario/completar_cadastro.html", informacoes)
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

class Perfil(LoginRequiredMixin, generic.UpdateView):
    model = Usuario
    template_name = 'Usuario/perfil.html'
    form_class = forms.FormEditarUsuario
    context_object_name = 'usuario'

    def get_object(self):
        return Usuario.objects.get(pk=self.request.user.pk)  # Correto, sempre o usuário autenticado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form_senha' not in context:
            context['form_senha'] = forms.FormEditarSenha(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        form_senha = forms.FormEditarSenha(user=request.user, data=request.POST)

        print("Entrou no post")

        # Verifica se é um POST de alteração de senha
        if request.POST.get('form_tipo') == 'senha':
            print("Entrou na senha")
            print("Old password:", request.POST.get('old_password'))
            print("New password1:", request.POST.get('new_password1'))
            print("New password2:", request.POST.get('new_password2'))
            if form_senha.is_valid():
                
                print("Válido")
                if not request.user.check_password(form_senha.cleaned_data['old_password']):
                    messages.error(request, 'Senha atual incorreta.')
                    context = self.get_context_data(form=form, form_senha=form_senha)
                    return self.render_to_response(context)

                request.user.set_password(form_senha.cleaned_data['new_password1'])
                request.user.save()

                update_session_auth_hash(request, request.user)  # Mantém logado
                messages.success(request, 'Senha atualizada com sucesso.')
                return redirect(self.get_success_url())

            else:
                print("erro")
                print("Erros do formulário:", form_senha.errors.as_data())
                messages.error(request, 'Erro ao atualizar a senha.')
                context = self.get_context_data(form=form, form_senha=form_senha)
                return self.render_to_response(context)

        elif request.POST.get('form_tipo') == 'perfil':
            
            print("Entrou no perfil")
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil atualizado com sucesso.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Erro ao atualizar o perfil.')
                return self.form_invalid(form)

        else:
            messages.error(request, 'Ação não reconhecida.')
            return redirect(self.get_success_url())


    def get_success_url(self):
        return reverse_lazy('usuario:perfil')

@method_decorator(csrf_exempt, name='dispatch')
def alterar_senha_ajax(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return JsonResponse({'status': 'success', 'mensagem': 'Senha atualizada com sucesso.'})
        else:
            erros = form.errors.as_json()
            return JsonResponse({'status': 'error', 'erros': erros})

    return JsonResponse({'status': 'error', 'mensagem': 'Método não permitido.'})

# class Perfil(LoginRequiredMixin, generic.UpdateView):
#     model = Usuario
#     template_name = 'Usuario/perfil.html'
#     form_class = forms.FormEditarUsuario
#     context_object_name = 'usuario'

#     def get_object(self):
#         return Usuario.objects.get(pk=self.request.user.pk)  # Sempre pega o próprio usuário

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['form_senha'] = forms.FormEditarSenha(user=Usuario.objects.get(pk=self.request.user.pk))
#         return context

#     def get_success_url(self):
#         return reverse_lazy('usuario:perfil')

class Editar(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Usuario
    form_class = forms.FormEditarUsuario
    template_name = 'Usuario/editar.html'

    def test_func(self):
        return self.request.user.id == self.get_object().id or self.request.user.is_superuser

    def get_success_url(self):
        return reverse_lazy("usuario:perfil")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        form_senha = forms.FormEditarSenha(user=request.user, data=request.POST)

        if 'new_password1' in request.POST and 'new_password2' in request.POST:
            if form_senha.is_valid():
                user = form_senha.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha atualizada com sucesso.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Erro ao atualizar a senha.')
                return self.form_invalid(form)
        else:
            if form.is_valid():
                messages.success(request, 'Perfil atualizado com sucesso.')
                return self.form_valid(form)
            else:
                messages.error(request, 'Erro ao atualizar o perfil.')
                return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_senha'] = forms.FormEditarSenha(user=self.request.user)
        return context

@login_required
def alterar_avatar(request, pk, novo):
    if (novo == 0):
        usuario = Usuario.objects.get(pk=pk)
        usuario.avatar = 'profile-pic/default.jpeg'
        usuario.save()
        return redirect('usuario:editar', pk=pk)
    else:
        pass

@login_required
def alterar_senha(request, pk, senha):
    usuario = Usuario.objects.get(pk=pk)
    usuario.password = make_password(senha)
    usuario.save()
    return redirect('usuario:editar', pk=pk)

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
        'form_filtro': form_filtro_acoes,
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

