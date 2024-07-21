from django import template
from PlanoAula.models import FotoRobo, FotoExecucao

register = template.Library()

@register.filter
def encontrar_usuario_lista(qs, usuario):
    lista = list(qs.values_list('usuario', flat=True))
    if usuario in lista:
        return True
    else:
        return False

@register.filter
def plano_aula_midias_foto(qs):
    fotos_robo = FotoRobo.objects.filter(plano_aula=qs)
    fotos_execucao = FotoExecucao.objects.filter(plano_aula=qs)

    resultado = []

    for foto in fotos_robo:
        resultado.append(foto.robo_foto.url)
    for foto in fotos_execucao:
        resultado.append(foto.execucao_foto.url)  
    return resultado