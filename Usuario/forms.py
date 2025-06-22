# from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.contrib.auth import forms as auth_forms
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import PasswordChangeForm

from Usuario.models import Usuario, Interesses
from Disciplina.models import Disciplina


class FormCriarUsuario(auth_forms.UserCreationForm):

    class Meta:
        fields = ('username', 'email', 'password1', 'password2')
        model = Usuario

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nome de usuário'
        self.fields['email'].label = 'E-mail'
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmar senha'

class FormCompletarCadastro(ModelForm):

    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'estado', 'cidade')

    def save(self, commit=True):
        user = super(FormCompletarCadastro, self).save(commit=False)
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super(FormCompletarCadastro, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['estado'].required = True
        self.fields['cidade'].required = True

class FormAtualizarInteresses(ModelForm):

    class Meta:
        model = Interesses
        fields = (('disciplina',))


class FormEditarUsuario(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'estado', 'cidade']

    def __init__(self, *args, **kwargs):
        super(FormEditarUsuario, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True  # Torna todos obrigatórios
            field.widget.attrs['class'] = 'form-control'


class FormEditarSenha(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super(FormEditarSenha, self).__init__(user, *args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''
            field.widget.attrs['class'] = 'form-control'
