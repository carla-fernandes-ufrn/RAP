import django_filters

from django.db.models import Q
from django import forms
from datetime import date

from Acoes.models import Acoes

class AcoesFiltro(django_filters.FilterSet):
    titulo = django_filters.CharFilter(lookup_expr='icontains')
    data_inicio = django_filters.DateFilter(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        lookup_expr='gt', label='Start Date'
    )
    data_fim = django_filters.DateFilter('data_fim')
    local = django_filters.CharFilter(lookup_expr='icontains')
    descricao = django_filters.CharFilter(lookup_expr='icontains')
    responsavel = django_filters.CharFilter(method='buscar_nome_completo')

    CHOICES = ((True, 'Sim'), (False, 'Não'))

    status = django_filters.BooleanFilter(
        widget=forms.RadioSelect(attrs={'class': 'form-control'}, choices=CHOICES),
        method='filtrar_status_personalizado'
    )

    def buscar_nome_completo(self, qs, name, value):
        for term in value.split():
            qs = qs.filter(Q(responsavel__first_name__icontains=term) | Q(responsavel__last_name__icontains=term))
        return qs

    def filtrar_status_personalizado(self, queryset, name, value):
        hoje = date.today()
        if value is True:
            # Está em execução: status=True E (data_fim > hoje OU data_fim é NULL)
            return queryset.filter(
                status=True
            ).filter(
                Q(data_fim__gte=hoje) | Q(data_fim__isnull=True)
            )
        elif value is False:
            # Não está em execução: status=False OU data_fim já passou
            return queryset.filter(
                Q(status=False) | Q(data_fim__lt=hoje)
            )
        return queryset

    class Meta:
        model = Acoes
        fields = {'tipo', 'formato'}