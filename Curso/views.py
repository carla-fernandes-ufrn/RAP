from django.shortcuts import render
from Disciplina.models import Disciplina, Conteudo

from django.contrib.auth.decorators import login_required

@login_required
def criar(request):
    disciplinas = Disciplina.objects.filter(status="Ativo")
    conteudos = Conteudo.objects.filter(status="Ativo")

    informacoes = {
        'disciplinas': disciplinas,
        'conteudos': conteudos,
    }

    return render(request, "Curso/criar.html", informacoes)