from django.contrib.auth import forms as auth_forms
from django import forms
from django.forms import ModelForm

from PlanoAula.models import PlanoAula, FotoRobo, VideoRobo, FotoExecucao, VideoExecucao, MensagemPlanoAula

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
        fields = ('robo_equipamento', 'robo_descricao', 'robo_link', 'robo_pdf')

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

class FormNovaMensagem(ModelForm):

    class Meta:
        model = MensagemPlanoAula
        fields = ('texto',)
    
    def save(self, commit=True):
        instance = super(FormNovaMensagem, self).save(commit=False)
        
        if commit:
            instance.save()
        return instance
