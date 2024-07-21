from django import template
from Usuario.models import Usuario

register = template.Library()

@register.simple_tag
def usuario_avatar(username):
    usuario_logado = Usuario.objects.filter(username=username)[0]
    return usuario_logado.avatar.url
