from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.hashers import make_password

from django.views import generic
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

from django.http import JsonResponse
from django.core import serializers
from django.db.models import RestrictedError

from Usuario import forms
from Usuario import filters as filter_usuarios
from Usuario.models import Usuario, Interesses
from Disciplina.models import Disciplina
from PlanoAula.models import PlanoAula
from PlanoAula import filters as filter_plano_aula
from Acoes.models import Acoes
from Acoes import filters as filter_acoes

import random
import time
from django.core.mail import send_mail
from django.conf import settings
from Usuario.models import CodigoValidacao
from Usuario.decorators import admin_otp_required

def is_admin_check(user):
    try:
        tipo = user.usuario.tipo_usuario
        return tipo in ['Administrador', 'Root'] or user.is_superuser
    except:
        return user.is_superuser

@method_decorator(admin_otp_required, name='dispatch')
class ListarAtivos(LoginRequiredMixin, UserPassesTestMixin, generic.ListView):
    model = Usuario
    template_name = 'Usuario/listar.html'
    context_object_name = 'lista_usuarios'
    paginate_by = 10

    def test_func(self):
        try:
            tipo = self.request.user.usuario.tipo_usuario
            return tipo in ['Administrador', 'Root'] or self.request.user.is_superuser
        except:
            return self.request.user.is_superuser

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
@admin_otp_required
@user_passes_test(is_admin_check)
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
@admin_otp_required
@user_passes_test(is_admin_check)
def listar_inativos(request):
    lista_usuarios = Usuario.objects.filter(is_active=False)
    
    informacoes = {
        'lista_usuarios': lista_usuarios,
        'ativos': False
    }

    return render(request, "Usuario/listar.html", informacoes)

@require_POST
@login_required
@admin_otp_required
@user_passes_test(is_admin_check)
def mudar_status(request, pk):
    if str(pk) == str(request.user.pk):
        messages.error(request, "Você não pode desativar sua própria conta.")
        return redirect('usuario:listar_ativos')
        
    usuario = Usuario.objects.get(pk=pk)
    
    # Root protection: Admin cannot deactivate Root
    req_is_root = False
    try:
        req_is_root = request.user.usuario.tipo_usuario == 'Root' or request.user.is_superuser
    except:
        req_is_root = request.user.is_superuser
        
    obj_is_root = False
    try:
        obj_is_root = usuario.tipo_usuario == 'Root' or usuario.is_superuser
    except:
        obj_is_root = usuario.is_superuser
        
    if obj_is_root and not req_is_root:
        messages.error(request, "Administradores não podem desativar usuários Root.")
        return redirect('usuario:listar_ativos')
        
    usuario.is_active = not usuario.is_active
    usuario.save()

    return redirect('usuario:listar_ativos')

@require_POST
@login_required
@admin_otp_required
@user_passes_test(is_admin_check)
def mudar_status_admin(request, pk):
    if str(pk) == str(request.user.pk):
        messages.error(request, "Você não pode alterar o cargo da sua própria conta.")
        return redirect('usuario:listar_ativos')
        
    usuario = Usuario.objects.get(pk=pk)
    
    # Root protection: Admin cannot demote Root
    req_is_root = False
    try:
        req_is_root = request.user.usuario.tipo_usuario == 'Root' or request.user.is_superuser
    except:
        req_is_root = request.user.is_superuser
        
    obj_is_root = False
    try:
        obj_is_root = usuario.tipo_usuario == 'Root' or usuario.is_superuser
    except:
        obj_is_root = usuario.is_superuser
        
    if obj_is_root and not req_is_root:
        messages.error(request, "Administradores não podem rebaixar usuários Root.")
        return redirect('usuario:listar_ativos')
        
    tipos = ['Aluno', 'Professor', 'Administrador']
    if req_is_root:
        tipos.append('Root')
        
    try:
        idx = tipos.index(usuario.tipo_usuario)
    except ValueError:
        idx = 0
        
    usuario.tipo_usuario = tipos[(idx + 1) % len(tipos)]
    
    if usuario.tipo_usuario in ['Administrador', 'Root']:
        usuario.is_superuser = True
    else:
        usuario.is_superuser = False
        
    usuario.save()
    
    return redirect('usuario:listar_ativos')

class Cadastrar(generic.CreateView):
    form_class = forms.FormCriarUsuario
    template_name = 'Usuario/cadastrar.html'
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        
        otp = str(random.randint(100000, 999999))
        CodigoValidacao.objects.create(usuario=user, codigo=otp, tipo='CADASTRO')
        
        print(f"\n==============================================")
        print(f"TOKEN DE CADASTRO PARA {user.email}: {otp}")
        print(f"==============================================\n")
        
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #28a745; padding: 20px; text-align: center;">
                <h2 style="color: white; margin: 0;">Robótica para Alunos e Professores</h2>
            </div>
            <div style="padding: 30px; text-align: center;">
                <h3 style="color: #333;">Confirmação de Cadastro</h3>
                <p style="color: #555; font-size: 16px;">Seu código de confirmação é:</p>
                <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #333;">{otp}</span>
                </div>
                <p style="color: #777; font-size: 14px;">Se você não se cadastrou no nosso sistema, por favor ignore este e-mail.</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 15px; text-align: center; border-top: 1px solid #e0e0e0;">
                <p style="color: #999; font-size: 12px; margin: 0;">Equipe Projeto RAP © 2026</p>
            </div>
        </div>
        """
        
        send_mail(
            subject='Confirmação de Cadastro - RAP',
            message=f'Seu código de confirmação é: {otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
            html_message=html_message
        )
        
        self.request.session['ativacao_user_id'] = user.id
        return redirect('usuario:ativar_email')

def ativar_email(request):
    user_id = request.session.get('ativacao_user_id')
    if not user_id:
        return redirect('usuario:login')
        
    try:
        user = Usuario.objects.get(id=user_id)
    except Usuario.DoesNotExist:
        return redirect('usuario:login')

    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        validacao = CodigoValidacao.objects.filter(usuario=user, codigo=codigo, tipo='CADASTRO', utilizado=False).last()
        if validacao:
            validacao.utilizado = True
            validacao.save()
            
            user.is_active = True
            user.save()
            messages.success(request, 'Email confirmado com sucesso! Você pode fazer login agora.')
            del request.session['ativacao_user_id']
            return redirect('usuario:login')
        else:
            messages.error(request, 'Código inválido ou já utilizado.')
            
    return render(request, 'Usuario/ativar_email.html', {'email': user.email})

@login_required
def validar_admin(request):
    user = request.user
    try:
        usuario_obj = user.usuario
    except:
        usuario_obj = Usuario.objects.get(pk=user.pk)
        
    if request.method == 'GET':
        otp = str(random.randint(100000, 999999))
        CodigoValidacao.objects.create(usuario=usuario_obj, codigo=otp, tipo='ADMIN')
        
        print(f"\n==============================================")
        print(f"TOKEN ADMIN (SUDO) PARA {user.email}: {otp}")
        print(f"==============================================\n")
        
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #dc3545; padding: 20px; text-align: center;">
                <h2 style="color: white; margin: 0;">Robótica para Alunos e Professores</h2>
            </div>
            <div style="padding: 30px; text-align: center;">
                <h3 style="color: #333;">Acesso Administrativo</h3>
                <p style="color: #555; font-size: 16px;">Seu código para acessar áreas sensíveis do sistema é:</p>
                <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #333;">{otp}</span>
                </div>
                <p style="color: #777; font-size: 14px;">Este código é válido por 1 hora. Se você não solicitou, verifique a segurança da sua conta.</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 15px; text-align: center; border-top: 1px solid #e0e0e0;">
                <p style="color: #999; font-size: 12px; margin: 0;">Equipe Projeto RAP © 2026</p>
            </div>
        </div>
        """
        
        send_mail(
            subject='Código de Acesso Administrativo - RAP',
            message=f'Seu código para acessar áreas sensíveis do sistema é: {otp}. Válido por 1 hora.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
            html_message=html_message
        )
        messages.info(request, f'Enviamos um código de 6 dígitos para o seu e-mail ({user.email}).')
        
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        validacao = CodigoValidacao.objects.filter(
            usuario=usuario_obj, 
            codigo=codigo, 
            tipo='ADMIN', 
            utilizado=False
        ).last()
        
        if validacao:
            validacao.utilizado = True
            validacao.save()
            
            request.session['admin_otp_valido_ate'] = time.time() + 3600
            
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Código incorreto.')
            
    return render(request, 'Usuario/validar_admin.html')

@login_required
def completar_cadastro(request):
    try:
        usuario = Usuario.objects.get(pk=request.user.pk)
    except Usuario.DoesNotExist:
        # Caso o usuário tenha sido criado via createsuperuser, ele existe em auth_user 
        # mas não na tabela usuario_usuario. Vamos criar a extensão agora usando SQL
        # direto para evitar os bugs de herança de múltiplas tabelas do Django ORM.
        from django.db import connection
        table_name = Usuario._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute(
                f'INSERT INTO "{table_name}" (user_ptr_id, cidade, estado, avatar) VALUES (%s, %s, %s, %s)',
                [request.user.pk, '', 'AC', 'profile-pic/default.jpeg']
            )
        usuario = Usuario.objects.get(pk=request.user.pk)

    # disciplinas ativas para lista de interesses
    disciplinas = Disciplina.objects.filter(status='Ativo')

    # ids de disciplinas já marcadas como interesse
    interesses_ids = list(
        Interesses.objects.filter(usuario=usuario).values_list('disciplina', flat=True)
    )

    if request.method == "POST":
        # edita o próprio usuário
        form_usuario = forms.FormCompletarCadastro(request.POST, instance=usuario)

        if form_usuario.is_valid():
            form_usuario.save()

            # trata hidden com lista de interesses (ex: "1,3,5")
            bruto = (request.POST.get('lista_interesses') or '').strip()
            novos_ids = set(int(x) for x in bruto.split(',') if x.strip().isdigit())
            antigos_ids = set(interesses_ids)

            # ADD interesses novos
            for disc_id in (novos_ids - antigos_ids):
                disciplina = Disciplina.objects.get(pk=disc_id)
                usuario.interesses.add(disciplina)

            # REMOVE interesses desmarcados
            for disc_id in (antigos_ids - novos_ids):
                disciplina = Disciplina.objects.get(pk=disc_id)
                Interesses.objects.filter(usuario=usuario, disciplina=disciplina).delete()

            return redirect('home')

        # POST inválido → volta pro template com erros
        contexto = {
            'form_usuario': form_usuario,
            'disciplinas': disciplinas,
            'interesses': interesses_ids,
        }
        # ⚠️ AQUI: respeita o nome/case real da pasta de template
        return render(request, "Usuario/completar_cadastro.html", contexto)

    # GET → mostra dados atuais
    form_usuario = forms.FormCompletarCadastro(instance=usuario)

    contexto = {
        'form_usuario': form_usuario,
        'disciplinas': disciplinas,
        'interesses': interesses_ids,
    }
    return render(request, "Usuario/completar_cadastro.html", contexto)

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
        try:
            return Usuario.objects.get(pk=self.request.user.pk)
        except Usuario.DoesNotExist:
            from django.db import connection
            table_name = Usuario._meta.db_table
            with connection.cursor() as cursor:
                cursor.execute(
                    f'INSERT INTO "{table_name}" (user_ptr_id, cidade, estado, avatar) VALUES (%s, %s, %s, %s)',
                    [self.request.user.pk, '', 'AC', 'profile-pic/default.jpeg']
                )
            return Usuario.objects.get(pk=self.request.user.pk)

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

@method_decorator(admin_otp_required, name='dispatch')
class Editar(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Usuario
    form_class = forms.FormEditarUsuario
    template_name = 'Usuario/editar.html'

    def test_func(self):
        try:
            is_admin = self.request.user.usuario.tipo_usuario == 'Administrador' or self.request.user.is_superuser
        except:
            is_admin = self.request.user.is_superuser
        return is_admin

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        try:
            is_root = self.request.user.usuario.tipo_usuario == 'Root' or self.request.user.is_superuser
        except:
            is_root = self.request.user.is_superuser
            
        if not is_root:
            if 'tipo_usuario' in form.fields:
                del form.fields['tipo_usuario']
        return form

    def get_success_url(self):
        return reverse_lazy("usuario:perfil")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        form_senha = forms.FormAdminSetPassword(user=self.object, data=request.POST)

        if 'new_password1' in request.POST and 'new_password2' in request.POST:
            if form_senha.is_valid():
                user = form_senha.save()
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
        context['form_senha'] = forms.FormAdminSetPassword(user=self.get_object())
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

@method_decorator(admin_otp_required, name='dispatch')
class DeletarUser(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
     model = Usuario
     template_name = 'Usuario/deletar.html'
     success_url = reverse_lazy('usuario:listar_ativos')

     def test_func(self):
         try:
             tipo = self.request.user.usuario.tipo_usuario
             return tipo in ['Administrador', 'Root'] or self.request.user.is_superuser
         except:
             return self.request.user.is_superuser

     def dispatch(self, request, *args, **kwargs):
         obj = self.get_object()
         if str(obj.pk) == str(request.user.pk):
             messages.error(request, "Você não pode excluir sua própria conta.")
             return redirect('usuario:listar_ativos')
             
         req_is_root = False
         try:
             req_is_root = request.user.usuario.tipo_usuario == 'Root' or request.user.is_superuser
         except:
             req_is_root = request.user.is_superuser
             
         obj_is_root = False
         try:
             obj_is_root = obj.tipo_usuario == 'Root' or obj.is_superuser
         except:
             obj_is_root = obj.is_superuser
             
         if obj_is_root and not req_is_root:
             messages.error(request, "Administradores não podem excluir usuários Root.")
             return redirect('usuario:listar_ativos')
             
         return super().dispatch(request, *args, **kwargs)
         
     def post(self, request, *args, **kwargs):
         # O método genérico 'delete' é chamado pelo post na DeleteView
         return self.delete(request, *args, **kwargs)
         
     def delete(self, request, *args, **kwargs):
         obj = self.get_object()
         
         # Limpar dependências inofensivas que não deveriam bloquear a exclusão
         obj.interesses_usuario.all().delete()
         
         if hasattr(obj, 'likes_plano_aula'):
             obj.likes_plano_aula.all().delete()
             
         if hasattr(obj, 'execucoes_plano_aula'):
             obj.execucoes_plano_aula.all().delete()
         
         try:
             response = super().delete(request, *args, **kwargs)
             messages.success(request, "Usuário excluído com sucesso.")
             return response
         except RestrictedError:
             messages.error(request, "Não é possível excluir este usuário pois ele é autor de conteúdos importantes (Planos de Aula, Ações, etc). Recomendamos apenas inativá-lo.")
             return redirect('usuario:listar_inativos')

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

def esqueceu_senha(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Por favor, insira um e-mail válido.')
            return render(request, 'Usuario/esqueceu_senha.html')
            
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            # Medida de segurança para não enumerar emails existentes no banco
            messages.success(request, 'Se o e-mail estiver cadastrado, um código foi enviado.')
            return redirect('usuario:login')

        otp = str(random.randint(100000, 999999))
        CodigoValidacao.objects.create(usuario=user, codigo=otp, tipo='RECUPERACAO')
        
        print(f"\n==============================================")
        print(f"TOKEN DE RECUPERAÇÃO PARA {user.email}: {otp}")
        print(f"==============================================\n")
        
        html_message = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="background-color: #0d6efd; padding: 20px; text-align: center;">
                <h2 style="color: white; margin: 0;">Robótica para Alunos e Professores</h2>
            </div>
            <div style="padding: 30px; text-align: center;">
                <h3 style="color: #333;">Recuperação de Senha</h3>
                <p style="color: #555; font-size: 16px;">Seu código para redefinir a senha é:</p>
                <div style="background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin: 25px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #333;">{otp}</span>
                </div>
                <p style="color: #777; font-size: 14px;">Se você não solicitou a redefinição de senha, por favor ignore este e-mail.</p>
            </div>
            <div style="background-color: #f8f9fa; padding: 15px; text-align: center; border-top: 1px solid #e0e0e0;">
                <p style="color: #999; font-size: 12px; margin: 0;">Equipe Projeto RAP © 2026</p>
            </div>
        </div>
        """
        
        send_mail(
            subject='Recuperação de Senha - RAP',
            message=f'Seu código para redefinir a senha é: {otp}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
            html_message=html_message
        )
        
        request.session['recuperacao_user_id'] = user.id
        return redirect('usuario:validar_recuperacao')

    return render(request, 'Usuario/esqueceu_senha.html')

def validar_recuperacao(request):
    user_id = request.session.get('recuperacao_user_id')
    if not user_id:
        return redirect('usuario:password_reset')
        
    try:
        user = Usuario.objects.get(id=user_id)
    except Usuario.DoesNotExist:
        return redirect('usuario:password_reset')

    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        validacao = CodigoValidacao.objects.filter(usuario=user, codigo=codigo, tipo='RECUPERACAO', utilizado=False).last()
        if validacao:
            validacao.utilizado = True
            validacao.save()
            
            request.session['redefinir_autorizado'] = user.id
            return redirect('usuario:redefinir_senha')
        else:
            messages.error(request, 'Código inválido ou já utilizado.')
            
    return render(request, 'Usuario/validar_recuperacao.html', {'email': user.email})

def redefinir_senha(request):
    user_id = request.session.get('redefinir_autorizado')
    if not user_id:
        return redirect('usuario:login')
        
    try:
        user = Usuario.objects.get(id=user_id)
    except Usuario.DoesNotExist:
        return redirect('usuario:login')

    if request.method == 'POST':
        form = forms.FormAdminSetPassword(user=user, data=request.POST)
        if form.is_valid():
            form.save()
            
            del request.session['redefinir_autorizado']
            if 'recuperacao_user_id' in request.session:
                del request.session['recuperacao_user_id']
                
            messages.success(request, 'Senha redefinida com sucesso! Você já pode fazer login.')
            return redirect('usuario:login')
    else:
        form = forms.FormAdminSetPassword(user=user)

    return render(request, 'Usuario/redefinir_senha.html', {'form': form})

