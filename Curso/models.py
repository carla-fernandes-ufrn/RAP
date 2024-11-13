from django.db import models
from django.utils import timezone

from Usuario.models import Usuario
from PlanoAula.models import PlanoAula

class Curso(models.Model):

    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT,null=True, verbose_name="Usuário")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    data_criacao = models.DateTimeField(default=timezone.now, verbose_name="Data de criação")
    quantidade_aulas = models.PositiveIntegerField(verbose_name="Quantidade de aulas")

    aulas = models.ManyToManyField(PlanoAula, related_name="aulas", through='Aulas', verbose_name="Aulas")

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['titulo']
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

class Aulas(models.Model):
    curso = models.ForeignKey(Curso, related_name='cursos', on_delete=models.RESTRICT, verbose_name="Curso")
    aula = models.ForeignKey(PlanoAula, related_name='cursos', on_delete=models.RESTRICT, verbose_name="Plano de aula")
    indice = models.PositiveIntegerField(verbose_name="Índice")
    
    def __str__(self):
        return str(self.indice) + " - " + self.aula.titulo

    class Meta:
        ordering = ['curso','indice']
        verbose_name = "Aula"
        verbose_name_plural = "Aulas"