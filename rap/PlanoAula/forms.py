from django.contrib.auth import forms as auth_forms
from django import forms
from django.forms import ModelForm

from PlanoAula.models import PlanoAula, FotoRobo, VideoRobo, FotoExecucao, VideoExecucao

class FormInfGerais(ModelForm):
        
    # required_css_class = 'required'

    class Meta:
        model = PlanoAula
        fields = ('titulo', 'contextualizacao', 'descricao_atividade', 'avaliacao')
    
        error_messages = {
            'titulo': {
                'required': "Esse campo é obrigatório.",
            }
        }

class FormMontagem(ModelForm):

    class Meta:
        model = PlanoAula
        fields = ('robo_equipamento', 'robo_descricao', 'robo_link')

class FormProgramacao(ModelForm):
    
    class Meta:
        model = PlanoAula
        fields = ('prog_linguagem', 'prog_descricao', 'prog_link', 'prog_codigos')

class FormMidiasRoboFotos(ModelForm):
    
    class Meta:
        model = FotoRobo
        fields = ('robo_foto',)
        widgets = {
            'robo_foto': forms.ClearableFileInput(attrs={'allow_multiple_selected': True}),
        }

class FormMidiasRoboVideos(ModelForm):
    
    class Meta:
        model = VideoRobo
        fields = ('robo_video',)
        widgets = {
            'robo_video': forms.ClearableFileInput(attrs={'allow_multiple_selected': True, 'accept': ".mp4, .avi, .wmv, .wkv, .mov"}),
        }

class FormMidiasRobo(ModelForm):
    
    class Meta:
        model = PlanoAula
        fields = ('robo_pdf',)

class FormMidiasExecucaoFotos(ModelForm):
    
    class Meta:
        model = FotoExecucao
        fields = ('execucao_foto',)
        widgets = {
            'execucao_foto': forms.ClearableFileInput(attrs={'allow_multiple_selected': True}),
        }

class FormMidiasExecucaoVideos(ModelForm):
    
    class Meta:
        model = VideoExecucao
        fields = ('execucao_video',)
        widgets = {
            'execucao_video': forms.ClearableFileInput(attrs={'allow_multiple_selected': True, 'accept': ".mp4, .avi, .wmv, .wkv, .mov"}),
        }


class FormEditarPlano_aula(ModelForm):
    titulo = forms.CharField(max_length=200, label='Titulo', widget=forms.Textarea)
    contextualizacao = forms.CharField(max_length=200, label='Contextualizacao', widget=forms.Textarea)
    descricao_atividade = forms.CharField(max_length=200, label='descricao da atividade', widget=forms.Textarea)

    class Meta:
        model = PlanoAula
        fields = ('titulo', 'contextualizacao', 'descricao_atividade')



    def save(self, commit=True):
        user = super(FormEditarPlano_aula, self).save(commit=False)

        if commit:
            user.save()
        return user
