# acervo/forms.py

from django import forms
from .models import Acervo

class AcervoForm(forms.ModelForm):
    class Meta:
        model = Acervo
        fields = [
            'titulo',
            'tipo',
            'descricao',
            'autor',
            'ano',
            'link',
            'file',
            'licenca_de_uso',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'licenca_de_uso': forms.TextInput(attrs={'class': 'form-control'}),
        }
