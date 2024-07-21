from django import forms
from django.forms import ModelForm

from Acoes.models import MensagemAcoes, Midia

class FormNovaMidia(ModelForm):

    midia = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'name': 'midia', 'id': 'midia', 'allow_multiple_selected': True})
    )

    class Meta:
        model = Midia
        fields = ('midia',)
    
    # def save(self, commit=True):
    #     instance = super(FormNovaMidia, self).save(commit=False)
        
    #     if commit:
    #         instance.save()
    #     return instance

class FormNovaMensagem(ModelForm):

    class Meta:
        model = MensagemAcoes
        fields = ('texto',)
    
    def save(self, commit=True):
        instance = super(FormNovaMensagem, self).save(commit=False)
        
        if commit:
            instance.save()
        return instance