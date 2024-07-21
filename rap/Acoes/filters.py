import django_filters

from django.db.models import Q

from Acoes.models import Acoes

class AcoesFiltro(django_filters.FilterSet):
    titulo = django_filters.CharFilter(lookup_expr='icontains')
    data_inicio = django_filters.DateFilter('data_inicio')
    data_fim = django_filters.DateFilter('data_fim')
    local = django_filters.CharFilter(lookup_expr='icontains')
    descricao = django_filters.CharFilter(lookup_expr='icontains')
    responsavel = django_filters.CharFilter(method='buscar_nome_completo')

    def buscar_nome_completo(self, qs, name, value):
        for term in value.split():
            qs = qs.filter(Q(responsavel__first_name__icontains=term) | Q(responsavel__last_name__icontains=term))
        return qs

    class Meta:
        model = Acoes
        fields = {'tipo', 'status'}