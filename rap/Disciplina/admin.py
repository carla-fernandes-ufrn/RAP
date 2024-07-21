from django.contrib import admin
from Disciplina import models

admin.site.register(models.Disciplina)
admin.site.register(models.Conteudo)
admin.site.register(models.SugestaoDisciplina)
admin.site.register(models.SugestaoConteudo)
