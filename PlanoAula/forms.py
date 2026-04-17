from django.contrib.auth import forms as auth_forms
from django import forms
from django.forms import ModelForm

from PlanoAula.models import PlanoAula, FotoRobo, VideoRobo, FotoExecucao, VideoExecucao, MensagemPlanoAula


class FormInfGerais(ModelForm):
    class Meta:
        model = PlanoAula
        fields = ('titulo', 'contextualizacao', 'descricao_atividade', 'avaliacao')
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: Introdução a sensores com robô seguidor de linha'
            }),
            'contextualizacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Explique o contexto pedagógico da aula, onde ela se encaixa e por que ela é importante.'
            }),
            'descricao_atividade': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Descreva o que será feito na aula, etapas, dinâmica, materiais e execução.'
            }),
            'avaliacao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Explique como a aprendizagem será avaliada.'
            }),
        }


class FormMontagem(ModelForm):
    class Meta:
        model = PlanoAula
        fields = (
            'nivel_dificuldade_montagem',
            'robo_equipamento',
            'robo_descricao',
            'robo_link',
            'robo_pdf'
        )
        widgets = {
            'nivel_dificuldade_montagem': forms.Select(attrs={
                'class': 'form-select'
            }),
            'robo_equipamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: Kit LEGO, Arduino, sensores, motores...'
            }),
            'robo_descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Descreva o robô, sua estrutura e finalidade.'
            }),
            'robo_link': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cole links úteis separados por linha.'
            }),
            'robo_pdf': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }


class FormProgramacao(ModelForm):
    class Meta:
        model = PlanoAula
        fields = (
            'nivel_dificuldade_programacao',
            'prog_linguagem',
            'prog_descricao',
            'prog_link',
            'prog_codigos'
        )
        widgets = {
            'nivel_dificuldade_programacao': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prog_linguagem': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: C++, Python, Blockly...'
            }),
            'prog_descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Descreva a lógica da programação utilizada na aula.'
            }),
            'prog_link': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cole links úteis separados por linha.'
            }),
            'prog_codigos': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

class FormMidiaRobo(forms.Form):
    arquivo = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*'
        })
    )


class FormMidiaExecucao(forms.Form):
    arquivo = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*'
        })
    )

class FormMidiasRoboFotos(ModelForm):
    class Meta:
        model = FotoRobo
        fields = ('robo_foto',)
        widgets = {
            'robo_foto': forms.ClearableFileInput(attrs={
                'allow_multiple_selected': True,
                'class': 'form-control'
            }),
        }


class FormMidiasRoboVideos(ModelForm):
    class Meta:
        model = VideoRobo
        fields = ('robo_video',)
        widgets = {
            'robo_video': forms.ClearableFileInput(attrs={
                'allow_multiple_selected': True,
                'accept': ".mp4, .avi, .wmv, .wkv, .mov",
                'class': 'form-control'
            }),
        }


class FormMidiasExecucaoFotos(ModelForm):
    class Meta:
        model = FotoExecucao
        fields = ('execucao_foto',)
        widgets = {
            'execucao_foto': forms.ClearableFileInput(attrs={
                'allow_multiple_selected': True,
                'class': 'form-control'
            }),
        }


class FormMidiasExecucaoVideos(ModelForm):
    class Meta:
        model = VideoExecucao
        fields = ('execucao_video',)
        widgets = {
            'execucao_video': forms.ClearableFileInput(attrs={
                'allow_multiple_selected': True,
                'accept': ".mp4, .avi, .wmv, .wkv, .mov",
                'class': 'form-control'
            }),
        }


class FormNovaMensagem(ModelForm):
    class Meta:
        model = MensagemPlanoAula
        fields = ('texto',)
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escreva sua mensagem...'
            })
        }

    def save(self, commit=True):
        instance = super(FormNovaMensagem, self).save(commit=False)

        if commit:
            instance.save()
        return instance