import django_filters
from PlanoAula.models import PlanoAula

class PlanoAulaFiltro(django_filters.FilterSet):
    titulo = django_filters.CharFilter(lookup_expr='icontains')
    contextualizacao = django_filters.CharFilter(lookup_expr='icontains')
    descricao_atividade = django_filters.CharFilter(lookup_expr='icontains')
    robo_equipamento = django_filters.CharFilter(lookup_expr='icontains')
    prog_linguagem = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = PlanoAula
        fields = {'conteudos', 'conteudos__disciplina'}