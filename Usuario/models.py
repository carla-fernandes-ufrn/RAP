from django.contrib.auth.models import User
from django.db import models

ESTADOS = [
    ('AC', 'Acre'),
    ('AL', 'Alagoas'),
    ('AP', 'Amapá'),
    ('AM', 'Amazonas'),
    ('BA', 'Bahia'),
    ('CE', 'Ceará'),
    ('DF', 'Distrito Federal'),
    ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'),
    ('MA', 'Maranhão'),
    ('MT', 'Mato Grosso'),
    ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'),
    ('PA', 'Pará'),
    ('PB', 'Paraíba'),
    ('PR', 'Paraná'),
    ('PE', 'Pernambuco'),
    ('PI', 'Piauí'),
    ('RJ', 'Rio de Janeiro'),
    ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'),
    ('RO', 'Rondônia'),
    ('RR', 'Roraima'),
    ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'),
    ('SE', 'Sergipe'),
    ('TO', 'Tocantins')
]

TIPO_USUARIO = [
    ('Aluno', 'Aluno'),
    ('Professor', 'Professor'),
    ('Administrador', 'Administrador'),
    ('Root', 'Root'),
]

class Usuario(User):
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='AC', verbose_name='Estado')
    avatar = models.ImageField(upload_to='profile-pic/', default='profile-pic/default.jpeg')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO, default='Aluno', verbose_name='Tipo de Usuário')
    interesses = models.ManyToManyField('Disciplina.Disciplina', through='Interesses')

    def __str__(self):
        return self.first_name + " " + self.last_name
    
    @property
    def planos_ativos_count(self):
        return self.planos_criados.filter(status=True).count()
    
    @property
    def acoes_cadastradas_count(self):
        return self.acoes_cadastradas.filter(deletada=False).count()

    @property
    def acoes_ativas_count(self):
        return self.acoes_cadastradas.filter(deletada=False, status=True).count()

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

class CodigoValidacao(models.Model):
    TIPO_CODIGO = [
        ('CADASTRO', 'Confirmação de Cadastro'),
        ('ADMIN', 'Ação Administrativa'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='codigos_validacao')
    codigo = models.CharField(max_length=6)
    tipo = models.CharField(max_length=10, choices=TIPO_CODIGO)
    criado_em = models.DateTimeField(auto_now_add=True)
    utilizado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario.username} - {self.tipo} - {self.codigo}"