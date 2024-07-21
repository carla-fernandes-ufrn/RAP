from django.contrib.auth.models import User
from django.db import models

class Usuario(User):
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=100, verbose_name='Estado')
    avatar = models.ImageField(upload_to='profile-pic/', default='profile-pic/default.jpeg')
    interesses = models.ManyToManyField('Disciplina.Disciplina', through='Interesses')

    def __str__(self):
        return self.first_name + " " + self.last_name

    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

class Interesses(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, related_name='interesses_usuario', verbose_name="Usuário")
    disciplina = models.ForeignKey('Disciplina.Disciplina', on_delete=models.RESTRICT, verbose_name="Disciplina")

    def __str__(self):
        return str(self.usuario.first_name) + " " + self.disciplina.nome

    class Meta:
        ordering = ['usuario', 'disciplina']
        verbose_name = "Interesse"
        verbose_name_plural = "Interesses"