from django.db import models

from Usuario.models import Usuario

STATUS = [
    ('Ativo', 'Ativo'),
    ('Inativo', 'Inativo'),
]

class Disciplina(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome")
    status = models.CharField(max_length=7, choices=STATUS, default='Ativo')
    
    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"

class Conteudo(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.RESTRICT, related_name="conteudos", verbose_name="Disciplina")
    status = models.CharField(max_length=7, choices=STATUS, default='Ativo')
    
    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['disciplina', 'nome']
        verbose_name = "Conteúdo"
        verbose_name_plural = "Conteúdos"


STATUS_SUGESTAO = [
    ('A', 'Em espera'),
    ('B', 'Aprovado'),
    ('C', 'Negado'),
]

class SugestaoDisciplina(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome")
    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=True, verbose_name="Usuário")
    status = models.CharField(max_length=1, choices=STATUS_SUGESTAO, default='A')
    comentarios = models.TextField(null=True, blank=True, verbose_name="Comentários")
    data = models.DateField(auto_now_add=True, verbose_name="Data de criação", null=True)
    
    def __str__(self):
        return self.nome + " - " + str(self.usuario)

    class Meta:
        ordering = ['status']
        verbose_name = "Sugestão de Disciplina"
        verbose_name_plural = "Sugestões de Disciplina"


class SugestaoConteudo(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome")
    disciplina = models.ForeignKey(Disciplina, on_delete=models.RESTRICT, null=True, verbose_name="Disciplina")
    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT, null=True, verbose_name="Usuário")
    status = models.CharField(max_length=1, choices=STATUS_SUGESTAO, default='A')
    comentarios = models.TextField(null=True, blank=True, verbose_name="Comentários")
    data = models.DateField(auto_now_add=True, verbose_name="Data de criação", null=True)
    
    def __str__(self):
        return self.nome + " - " + str(self.usuario)

    class Meta:
        ordering = ['status']
        verbose_name = "Sugestão de Conteúdo"
        verbose_name_plural = "Sugestões de Conteúdo"
