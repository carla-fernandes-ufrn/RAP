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

class Usuario(User):
    cidade = models.CharField(max_length=100, verbose_name='Cidade')
    estado = models.CharField(max_length=2, choices=ESTADOS, default='AC', verbose_name='Estado')
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