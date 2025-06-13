# acervo/models.py

from django.db import models
from django.contrib.auth.models import User

class Acervo(models.Model):
    """
    Modelo unificado para representar itens do acervo.

    'tipo' agora é um CharField com choices, 
    não há mais uma segunda classe (TipoAcervo).
    O usuário escolhe diretamente o tipo ao criar/editar o acervo.
    """

    # Definições de constantes de tipo dentro da mesma classe
    ARTIGO = 'Artigo'
    TESE = 'Tese'
    DISSERTACAO = 'Dissertação'
    SOFTWARE = 'Software'
    HARDWARE = 'Hardware'
    KIT = 'Kit'
    OUTRO = 'Outro'

    TIPO_CHOICES = [
        (ARTIGO, 'Artigo'),
        (TESE, 'Tese'),
        (DISSERTACAO, 'Dissertação'),
        (SOFTWARE, 'Software'),
        (HARDWARE, 'Hardware'),
        (KIT, 'Kit'),
        (OUTRO, 'Outro'),
    ]

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default=OUTRO,  # Valor padrão se o usuário não escolher outro tipo
        help_text="Selecione o tipo de material do acervo."
    )

    titulo = models.CharField(
        max_length=255,
        help_text="Título ou nome do item do acervo."
    )

    descricao = models.TextField(
        help_text="Breve descrição do conteúdo ou características do item."
    )

    autor = models.CharField(
        max_length=255,
        help_text="Autor ou criador principal do item."
    )

    ano = models.PositiveIntegerField(
        default=2024,
        help_text="Ano de publicação/criação do item."
    )

    link = models.URLField(
        blank=True,
        null=True,
        help_text="Link para acesso online (opcional)."
    )

    file = models.FileField(
        upload_to='acervo_files/',
        blank=True,
        null=True,
        help_text="Arquivo local associado ao item, se houver."
    )

    licenca_de_uso = models.CharField(
        max_length=255,
        default='Sem Licença',
        help_text="Tipo de licença ou permissão de uso."
    )

    responsavel = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Usuário responsável por submeter este item ao acervo."
    )

    data_adicao = models.DateField(
        auto_now_add=True,
        help_text="Data de adição do item no sistema."
    )

    def __str__(self):
        return self.titulo
