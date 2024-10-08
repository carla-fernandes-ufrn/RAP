# Generated by Django 4.2.14 on 2024-07-25 13:48

import PlanoAula.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Disciplina', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExecucaoPlanoAula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Execução',
                'verbose_name_plural': 'Execuções',
                'ordering': ['usuario'],
            },
        ),
        migrations.CreateModel(
            name='FotoExecucao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execucao_foto', models.ImageField(upload_to=PlanoAula.models.diretorio_plano_aula_midias, verbose_name='Fotos da execução da atividade')),
            ],
            options={
                'verbose_name': 'Foto da execução',
                'verbose_name_plural': 'Fotos da execução',
                'ordering': ['-plano_aula__data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='FotoRobo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('robo_foto', models.ImageField(upload_to=PlanoAula.models.diretorio_plano_aula_midias, verbose_name='Fotos do robô')),
            ],
            options={
                'verbose_name': 'Foto do robô',
                'verbose_name_plural': 'Fotos do robô',
                'ordering': ['-plano_aula__data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='LikePlanoAula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Like',
                'verbose_name_plural': 'Likes',
                'ordering': ['usuario'],
            },
        ),
        migrations.CreateModel(
            name='MensagemPlanoAula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('texto', models.TextField(verbose_name='Texto')),
                ('data', models.DateTimeField(auto_now_add=True, verbose_name='Data')),
            ],
            options={
                'verbose_name': 'Mensagem',
                'verbose_name_plural': 'Mensagens',
                'ordering': ['plano_aula', 'mensagem_original__pk', '-data'],
            },
        ),
        migrations.CreateModel(
            name='PlanoAula',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_criacao', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data de criação')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('contextualizacao', models.TextField(verbose_name='Contextualização')),
                ('descricao_atividade', models.TextField(verbose_name='Descrição da atividade')),
                ('avaliacao', models.TextField(blank=True, null=True, verbose_name='Critérios de avaliação')),
                ('robo_equipamento', models.CharField(blank=True, max_length=200, null=True, verbose_name='Equipamento')),
                ('robo_descricao', models.TextField(blank=True, null=True, verbose_name='Descrição do robô')),
                ('robo_link', models.TextField(blank=True, null=True, verbose_name='Links')),
                ('prog_linguagem', models.CharField(blank=True, max_length=200, null=True, verbose_name='Linguagem de programação')),
                ('prog_descricao', models.TextField(blank=True, null=True, verbose_name='Descrição da programação')),
                ('prog_link', models.TextField(blank=True, null=True, verbose_name='Links')),
                ('prog_codigos', models.FileField(blank=True, null=True, upload_to=PlanoAula.models.diretorio_plano_aula, verbose_name='Códigos')),
                ('robo_pdf', models.FileField(blank=True, null=True, upload_to=PlanoAula.models.diretorio_plano_aula, verbose_name='Manual de montagem do robô')),
                ('conteudos', models.ManyToManyField(related_name='planos_de_aula', to='Disciplina.conteudo', verbose_name='Conteúdos')),
            ],
            options={
                'verbose_name': 'Plano de aula',
                'verbose_name_plural': 'Planos de aula',
                'ordering': ['titulo'],
            },
        ),
        migrations.CreateModel(
            name='VideoRobo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('robo_video', models.FileField(upload_to=PlanoAula.models.diretorio_plano_aula_midias, verbose_name='Vídeos do robô')),
                ('plano_aula', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='videos_robo', to='PlanoAula.planoaula', verbose_name='Plano de aula')),
            ],
            options={
                'verbose_name': 'Vídeo do robô',
                'verbose_name_plural': 'Vídeos do robô',
                'ordering': ['-plano_aula__data_criacao'],
            },
        ),
        migrations.CreateModel(
            name='VideoExecucao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execucao_video', models.FileField(upload_to=PlanoAula.models.diretorio_plano_aula_midias, verbose_name='Vídeos da execução da atividade')),
                ('plano_aula', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='videos_execucao', to='PlanoAula.planoaula', verbose_name='Plano de aula')),
            ],
            options={
                'verbose_name': 'Vídeo da execução',
                'verbose_name_plural': 'Vídeos da execução',
                'ordering': ['-plano_aula__data_criacao'],
            },
        ),
    ]
