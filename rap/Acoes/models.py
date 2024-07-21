from django.db import models
from datetime import date
from django.utils import timezone

from Usuario.models import Usuario

TIPO = [
    ('Evento', 'Evento'),
    ('Curso', 'Curso'),
    ('Palestra', 'Palestra'),
    ('Outro', 'Outro')
]

def user_directory_path(instance, filename):
    return 'user_{0}/acao_{1}/{2}'.format(instance.acao.responsavel.id, instance.acao.id, filename)


class Acoes(models.Model):
    titulo = models.CharField(max_length=500, verbose_name="Título")
    tipo = models.CharField(max_length=8, choices=TIPO, default='Evento')
    data_inicio = models.DateField(default = date.today, verbose_name = "Data de início")
    data_fim = models.DateField(null=True, blank = True, verbose_name = "Data de fim")
    local = models.CharField(max_length=200, null=True, blank=True, verbose_name="Local")
    descricao = models.TextField(null=True, blank=True,verbose_name="Descrição")
    responsavel = models.ForeignKey(Usuario, on_delete=models.RESTRICT,verbose_name="Responsável")
    status = models.BooleanField(default=True, verbose_name = "Está em execução")
    deletada = models.BooleanField(default=False, verbose_name = "Deletado")

    def __str__(self):
        return str(self.tipo) + " - " + str(self.titulo)

    class Meta:
        ordering = ['-status', '-data_inicio', '-data_fim', 'titulo']
        verbose_name = "Ação"
        verbose_name_plural = "Ações"

class Midia(models.Model):
    acao = models.ForeignKey(Acoes, on_delete=models.RESTRICT,verbose_name="Ação", related_name='midias')
    midia = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    data = models.DateTimeField(verbose_name = "Data", auto_now_add=True)

    def __str__(self):
        return str(self.acao)

    class Meta:
        ordering = ['acao', 'data']
        verbose_name = "Mídia"
        verbose_name_plural = "Mídias"

class MensagemAcoes(models.Model):
    texto = models.TextField(verbose_name="Texto")
    data = models.DateTimeField(verbose_name = "Data", auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT,verbose_name="Usuário")
    acao = models.ForeignKey(Acoes, on_delete=models.RESTRICT,verbose_name="Ação")
    mensagem_original = models.ForeignKey('self', null=True, blank = True, related_name='replies', on_delete=models.CASCADE,verbose_name="Mensagem original")

    def __str__(self):
        return str(self.acao) + " - " + str(self.data)

    class Meta:
        ordering = ['acao', 'mensagem_original__pk', '-data']
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"