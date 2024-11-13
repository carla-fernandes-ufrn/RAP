from django import template
register = template.Library()

@register.filter
def nome_arquivo(value, key):
  return value.split(key)[3]