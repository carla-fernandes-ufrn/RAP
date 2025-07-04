from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator

from Usuario.models import Usuario
from Disciplina.models import Conteudo

def user_directory_path(instance, filename):
    return 'user_{0}/plano_aula_{1}/{2}'.format(instance.responsavel.id, instance.data_criacao, filename)

def diretorio_plano_aula(instance, filename):
    return 'plano_aula_{0}_{1}/{2}'.format(instance.data_criacao.date(), instance.data_criacao.strftime("%H-%M-%S"), filename)

def diretorio_plano_aula_midias(instance, filename):
    return 'plano_aula_{0}_{1}/{2}'.format(instance.plano_aula.data_criacao.date(), instance.plano_aula.data_criacao.strftime("%H-%M-%S"), filename)

NIVEL_DIFICULDADE = [
    ('Fácil', 'Fácil'),
    ('Intermediário', 'Intermediário'),
    ('Difícil', 'Difícil')
]

class PlanoAula(models.Model):

    criador = models.ForeignKey(Usuario, on_delete=models.RESTRICT,null=True, verbose_name="Responsável", related_name="planos_criados")
    data_criacao = models.DateTimeField(default=timezone.now, verbose_name="Data de criação")     

    # Gerais
    titulo = models.CharField(max_length=200, verbose_name="Título", blank=False, null=False)
    contextualizacao = models.TextField(verbose_name="Contextualização", blank=False, null=False)
    descricao_atividade = models.TextField(verbose_name="Descrição da atividade", blank=False, null=False)
    avaliacao = models.TextField(verbose_name="Critérios de avaliação", blank=True, null=True)
    conteudos = models.ManyToManyField(Conteudo, related_name="planos_de_aula", verbose_name="Conteúdos")

    # Montagem
    robo_equipamento = models.CharField(max_length=200, blank=True, null=True, verbose_name="Equipamento")
    robo_descricao = models.TextField(blank=True, null=True, verbose_name="Descrição do robô")
    robo_link = models.TextField(verbose_name="Links", blank=True, null=True)
    nivel_dificuldade_montagem = models.CharField(max_length=13, choices=NIVEL_DIFICULDADE, blank=True, null=True, verbose_name="Nível de dificuldade da montagem")

    # Programação
    prog_linguagem = models.CharField(max_length=200, blank=True, null=True, verbose_name="Linguagem de programação")
    prog_descricao = models.TextField(blank=True, null=True, verbose_name="Descrição da programação")
    prog_link = models.TextField(verbose_name="Links", blank=True, null=True)
    prog_codigos = models.FileField(upload_to=diretorio_plano_aula, blank=True, null=True, verbose_name="Códigos")
    nivel_dificuldade_programacao = models.CharField(max_length=13, choices=NIVEL_DIFICULDADE, blank=True, null=True, verbose_name="Nível de dificuldade da programação")

    # Mídias
    robo_pdf = models.FileField(upload_to=diretorio_plano_aula, blank=True, null=True, verbose_name="Manual de montagem do robô")

    status = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ['titulo']
        verbose_name = "Plano de aula"
        verbose_name_plural = "Planos de aula"

class FotoRobo(models.Model):
    plano_aula = models.ForeignKey(PlanoAula, related_name='fotos_robo', on_delete=models.RESTRICT, verbose_name="Plano de aula")
    robo_foto = models.ImageField(upload_to=diretorio_plano_aula_midias, verbose_name="Fotos do robô")

    def __str__(self):
        return str(self.plano_aula)

    class Meta:
        ordering = ['-plano_aula__data_criacao']
        verbose_name = "Foto do robô"
        verbose_name_plural = "Fotos do robô"

class VideoRobo(models.Model):
    plano_aula = models.ForeignKey(PlanoAula, related_name='videos_robo', on_delete=models.RESTRICT, verbose_name="Plano de aula")
    robo_video = models.FileField(upload_to=diretorio_plano_aula_midias, verbose_name="Vídeos do robô")

    def __str__(self):
        return str(self.plano_aula)

    class Meta:
        ordering = ['-plano_aula__data_criacao']
        verbose_name = "Vídeo do robô"
        verbose_name_plural = "Vídeos do robô"

class FotoExecucao(models.Model):
    plano_aula = models.ForeignKey(PlanoAula, related_name='fotos_execucao', on_delete=models.RESTRICT, verbose_name="Plano de aula")
    execucao_foto = models.ImageField(upload_to=diretorio_plano_aula_midias, verbose_name="Fotos da execução da atividade")

    def __str__(self):
        return str(self.plano_aula)

    class Meta:
        ordering = ['-plano_aula__data_criacao']
        verbose_name = "Foto da execução"
        verbose_name_plural = "Fotos da execução"

class VideoExecucao(models.Model):
    plano_aula = models.ForeignKey(PlanoAula, related_name='videos_execucao', on_delete=models.RESTRICT, verbose_name="Plano de aula")
    execucao_video = models.FileField(upload_to=diretorio_plano_aula_midias, verbose_name="Vídeos da execução da atividade")

    def __str__(self):
        return str(self.plano_aula)

    class Meta:
        ordering = ['-plano_aula__data_criacao']
        verbose_name = "Vídeo da execução"
        verbose_name_plural = "Vídeos da execução"

class LikePlanoAula(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT,null=True, verbose_name="Usuário", related_name="likes_plano_aula")
    plano_aula = models.ForeignKey(PlanoAula, related_name='likes', on_delete=models.RESTRICT,null=True, verbose_name="Plano de aula")

    def __str__(self):
        return str(self.usuario.first_name) + " - " + str(self.plano_aula.titulo)

    class Meta:
        ordering = ['usuario']
        verbose_name = "Like"
        verbose_name_plural = "Likes"

class ExecucaoPlanoAula(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT,null=True, verbose_name="Usuário", related_name="execucoes_plano_aula")
    plano_aula = models.ForeignKey(PlanoAula, related_name='execucoes', on_delete=models.RESTRICT,null=True, verbose_name="Plano de aula")

    def __str__(self):
        return str(self.usuario.first_name) + " - " + str(self.plano_aula.titulo)

    class Meta:
        ordering = ['usuario']
        verbose_name = "Execução"
        verbose_name_plural = "Execuções"

class MensagemPlanoAula(models.Model):
    texto = models.TextField(verbose_name="Texto")
    data = models.DateTimeField(verbose_name = "Data", auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.RESTRICT,verbose_name="Usuário")
    plano_aula = models.ForeignKey(PlanoAula, related_name='mensagens', on_delete=models.CASCADE,verbose_name="Plano de aula")
    mensagem_original = models.ForeignKey('self', null=True, blank = True, related_name='replies', on_delete=models.CASCADE,verbose_name="Mensagem original")

    def __str__(self):
        return str(self.plano_aula) + " - " + str(self.data)

    class Meta:
        ordering = ['plano_aula', 'mensagem_original__pk', '-data']
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"