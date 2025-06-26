from django import template
from Usuario.models import Usuario

register = template.Library()

@register.simple_tag
def usuario_avatar(username):
    usuario_logado = Usuario.objects.filter(username=username)[0]
    return usuario_logado.avatar.url

@register.filter
def iniciais_nome_completo(user):
    if not user.first_name and not user.last_name:
        return ""
    primeira = user.first_name.strip()[0] if user.first_name else ""
    ultima = user.last_name.strip()[0] if user.last_name else ""
    return f"{primeira.upper()}{ultima.upper()}"
