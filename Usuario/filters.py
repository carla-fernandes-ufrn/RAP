import django_filters

from django.db.models import Q
from django import forms

from Usuario.models import Usuario

class UsuarioFiltro(django_filters.FilterSet):
    nome = django_filters.CharFilter(method='buscar_nome_completo')
    cidade = django_filters.CharFilter(lookup_expr='icontains')
    
    def buscar_nome_completo(self, qs, name, value):
        for term in value.split():
            qs = qs.filter(Q(first_name__icontains=term) | Q(last_name__icontains=term))
        return qs

    class Meta:
        model = Usuario
        fields = {'estado'}