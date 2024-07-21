# from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.contrib.auth import forms as auth_forms
from django import forms
from django.forms import ModelForm

from Usuario.models import Usuario, Interesses
from Disciplina.models import Disciplina


class FormCriarUsuario(auth_forms.UserCreationForm):

    class Meta:
        # fields = ('username', 'first_name', 'last_name', 'email', 'cidade', 'estado', 'password1', 'password2')
        fields = ('username', 'email', 'password1', 'password2')
        model = Usuario

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['first_name'].label = 'Nome'
        # self.fields['last_name'].label = 'Sobrenome'
        self.fields['username'].label = 'Nome de usuário'
        self.fields['email'].label = 'E-mail'
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmar senha'

class FormCompletarCadastro(ModelForm):

    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'cidade', 'estado')

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(FormCompletarCadastro, self).save(commit=False)
        if commit:
            user.save()
        return user

class FormAtualizarInteresses(ModelForm):

    # disciplina = forms.ModelChoiceField(label='Disciplinas', queryset=Disciplina.objects.all(), widget=forms.CheckboxSelectMultiple)
    # disciplina = forms.ModelMultipleChoiceField(label='Disciplinas', 
                                                # queryset=Disciplina.objects.all(), 
                                                # widget=forms.CheckboxSelectMultiple(attrs={'style': 'list-style:none;'}))

    class Meta:
        model = Interesses
        fields = (('disciplina',))
        # widgets = {
        #     'disciplina' : forms.CheckboxInput(attrs={'class': 'checkbox form-control', 'style': 'list-style:none;'}),   
        # }


class FormEditarUsuario(ModelForm):
    # password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    # password2 = forms.CharField(label='Confirmar senha', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'cidade', 'estado', 'avatar')

    # def clean_password2(self):
    #     # Check that the two password entries match
    #     password1 = self.cleaned_data.get("password1")
    #     password2 = self.cleaned_data.get("password2")
    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError("As senhas estão incorretas.")
    #     return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(FormEditarUsuario, self).save(commit=False)
        # user.set_password(self.cleaned_data["password1"])
        # user.active = False # send confirmation email
        if commit:
            user.save()
        return user

class FormEditarSenha(ModelForm):
    password1 = forms.CharField(label='Senha', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar senha', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('password1', 'password2')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("As senhas estão incorretas.")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(FormEditarUsuario, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        # user.active = False # send confirmation email
        if commit:
            user.save()
        return user