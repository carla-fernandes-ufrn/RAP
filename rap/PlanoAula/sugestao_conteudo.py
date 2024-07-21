from Disciplina.models import Disciplina, Conteudo
from PlanoAula.models import PlanoAula, LikePlanoAula, ExecucaoPlanoAula
from Usuario.models import Usuario

def sugestao_planos_aula(usuario, quantidade):
    # Critério 1: disciplinas de interesse
    # Define os dois pré-requisitos:
    # 1- Identifica os planos de aula que não foram criados pelo usuário
    # 2- Identifica os planos de aula que não foram executados pelo usuário
    # Encontra planos de aula das disciplinas de interesse
    # Ordena os planos de aula
    lista_disciplinas_interesse = disciplinas_interesse(usuario.id, [])
    lista = PlanoAula.objects.all().exclude(responsavel=usuario)
    executados = ExecucaoPlanoAula.objects.filter(usuario=usuario).values_list('plano_aula')
    lista_pa_pre_requisitos = [x for x in lista if x not in executados]
    planos_aula_c1 = encontrar_planos_aula_por_disciplina(lista_disciplinas_interesse, quantidade, lista_pa_pre_requisitos)
    planos_aula_c1 = ordenar(planos_aula_c1)
    planos_aula = planos_aula_c1
    
    if len(planos_aula) == quantidade:
        return planos_aula
    else:
        # Critério 2: disciplinas de planos de aula favoritados
        # Identifica planos de aula que cumprem pré-requisitos mas que não foram analisados no C1
        # Encontra planos de aula das disciplinas favoritadas
        # Ordena os planos de aula
        lista_disciplinas_favoritadas = disciplinas_favoritadas(usuario.id, 
                                                          lista_disciplinas_interesse)
        lista_criterio_2 = [x for x in lista_pa_pre_requisitos if 
                            x not in planos_aula]
        planos_aula_c2 = encontrar_planos_aula_por_disciplina(
            lista_disciplinas_favoritadas, 
            quantidade-len(planos_aula), 
            lista_criterio_2)
        planos_aula_c2 = ordenar(planos_aula_c2)
        planos_aula.extend(planos_aula_c2)

        if len(planos_aula) == quantidade:
            return planos_aula
        else:
            # Critério 3: disciplinas de planos de aula executados
            # Identifica planos de aula que cumprem pré-requisitos mas que não foram analisados no C1 e C2
            # Encontra planos de aula das disciplinas executadas
            # Ordena os planos de aula
            lista_disciplinas_executadas = disciplinas_executadas(usuario.id, 
                                                            lista_disciplinas_interesse + lista_disciplinas_favoritadas)
            lista_criterio_3 = [x for x in lista_pa_pre_requisitos if 
                                x not in planos_aula]
            planos_aula_c3 = encontrar_planos_aula_por_disciplina(
                lista_disciplinas_executadas, 
                quantidade-len(planos_aula), 
                lista_criterio_3)
            planos_aula_c3 = ordenar(planos_aula_c3)
            planos_aula.extend(planos_aula_c3)

            if len(planos_aula) == quantidade:
                return planos_aula
            else:
                # Critério 4: todas as disciplinas
                # Identifica planos de aula que cumprem pré-requisitos mas que não foram analisados no C1 e C2
                # Encontra planos de aula das disciplinas executadas
                # Ordena os planos de aula
                lista_todas_disciplinas = todas_disciplinas(lista_disciplinas_interesse + lista_disciplinas_favoritadas + lista_disciplinas_executadas)
                lista_criterio_4 = [x for x in lista_pa_pre_requisitos if 
                                    x not in planos_aula]
                planos_aula_c4 = encontrar_planos_aula_por_disciplina(
                    lista_todas_disciplinas, 
                    quantidade-len(planos_aula), 
                    lista_criterio_4)
                planos_aula_c4 = ordenar(planos_aula_c4)
                planos_aula.extend(planos_aula_c4)

                return planos_aula

def definir_possiveis_planos_aula(planos_aula, remover):
    return [x for x in planos_aula if x not in remover]

def ordenar(lista_planos_aula):
    inf_planos_aula = []

    for plano_aula in lista_planos_aula:
        likes = list(LikePlanoAula.objects.filter(plano_aula=plano_aula).values_list('usuario', flat=True))
        execucoes = list(ExecucaoPlanoAula.objects.filter(plano_aula=plano_aula).values_list('usuario', flat=True))

        quantidade_likes_execucoes = 0
        if (len(likes) > len(execucoes)):
            for item in execucoes:
                if (len(LikePlanoAula.objects.filter(usuario__id=item, plano_aula=plano_aula))>0):
                    quantidade_likes_execucoes += 1
        else:
            for item in likes:
                if (len(ExecucaoPlanoAula.objects.filter(usuario__id=item, plano_aula=plano_aula))>0):
                    quantidade_likes_execucoes += 1
        quantidade_likes = len(likes)
        quantidade_execucoes = len(execucoes)
        inf_planos_aula.append([plano_aula, quantidade_likes_execucoes, 
                                quantidade_likes, quantidade_execucoes])
    
    inf_planos_aula.sort(key = lambda x: (x[1], x[2], x[3]), reverse=True)
    lista_ordenada = [x[0] for x in inf_planos_aula]

    return lista_ordenada

def encontrar_planos_aula_por_disciplina(lista_disciplinas, quantidade, lista_planos_aula):
    planos_aula_disciplina = []
    for plano_aula in lista_planos_aula:
        for item in plano_aula.conteudos.all():
            if item.disciplina in lista_disciplinas and plano_aula not in planos_aula_disciplina:
                planos_aula_disciplina.append(plano_aula)
    
    planos_aula_disciplina = ordenar(planos_aula_disciplina)
    
    if (len(planos_aula_disciplina) >= quantidade):
        return planos_aula_disciplina[0:quantidade]
    else:
        return planos_aula_disciplina

def disciplinas_interesse(usuario_id, remover):
    usuario = Usuario.objects.get(pk=usuario_id)

    disciplinas_interesse = [x for x in list(usuario.interesses.all()) if x not in remover]
    return disciplinas_interesse

def disciplinas_favoritadas(usuario_id, remover):
    usuario = Usuario.objects.get(pk=usuario_id)
    planos_aula_favoritados = LikePlanoAula.objects.filter(usuario=usuario).values_list('plano_aula')
    disciplinas = []
    for plano_aula_id in planos_aula_favoritados:
        plano_aula = PlanoAula.objects.get(id=plano_aula_id[0])

        for item in list(plano_aula.conteudos.all()):
            if item.disciplina not in disciplinas:
                disciplinas.append(item.disciplina)
    disciplinas_favoritadas = [x for x in disciplinas if x not in remover]
    return disciplinas_favoritadas

def disciplinas_executadas(usuario_id, remover):
    usuario = Usuario.objects.get(pk=usuario_id)
    planos_aula_executados = ExecucaoPlanoAula.objects.filter(usuario=usuario).values_list('plano_aula')
    disciplinas = []
    for plano_aula_id in planos_aula_executados:
        plano_aula = PlanoAula.objects.get(id=plano_aula_id[0])

        for item in list(plano_aula.conteudos.all()):
            if item.disciplina not in disciplinas:
                disciplinas.append(item.disciplina)
    disciplinas_executadas = [x for x in disciplinas if x not in remover]
    return disciplinas_executadas

def todas_disciplinas(remover):
    disciplinas = list(Disciplina.objects.filter(status='Ativo'))
    todas_disciplinas = [x for x in disciplinas if x not in remover]

    return todas_disciplinas

def definir_disciplinas_por_categoria(usuario_id, categoria):
    usuario = Usuario.objects.get(pk=usuario_id)

    disciplinas_interesse = list(usuario.interesses.all())

    if categoria == "interesse":
        return disciplinas_interesse

    planos_aula_favoritados = LikePlanoAula.objects.filter(usuario=usuario).values_list('plano_aula')
    disciplinas = []
    for plano_aula_id in planos_aula_favoritados:
        plano_aula = PlanoAula.objects.get(id=plano_aula_id[0])

        for item in list(plano_aula.conteudos.all()):
            if item.disciplina not in disciplinas:
                disciplinas.append(item.disciplina)
    disciplinas_favoritadas = [x for x in disciplinas if x not in disciplinas_interesse]

    if categoria == "favoritos":
        return disciplinas_favoritadas

    planos_aula_executados = ExecucaoPlanoAula.objects.filter(usuario=usuario).values_list('plano_aula')
    disciplinas = []
    for plano_aula_id in planos_aula_executados:
        plano_aula = PlanoAula.objects.get(id=plano_aula_id[0])

        for item in list(plano_aula.conteudos.all()):
            if item.disciplina not in disciplinas:
                disciplinas.append(item.disciplina)
    disciplinas_executadas = [x for x in disciplinas 
                       if x not in disciplinas_interesse and
                       x not in disciplinas_favoritadas]

    if categoria == "executadas":
        return disciplinas_executadas

    disciplinas = list(Disciplina.objects.filter(status='Ativo'))
    todas_disciplinas = [x for x in disciplinas 
                         if x not in disciplinas_interesse and 
                         x not in disciplinas_favoritadas and
                         x not in disciplinas_executadas]

    return todas_disciplinas