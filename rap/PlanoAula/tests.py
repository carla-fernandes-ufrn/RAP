from django.test import TestCase
from PlanoAula.models import PlanoAula, LikePlanoAula, ExecucaoPlanoAula
from Disciplina.models import Conteudo, Disciplina
from Usuario.models import Usuario, Interesses

from PlanoAula import views as planos_aula_views
from PlanoAula import sugestao_conteudo as sc

class PlanoAulaTests(TestCase):
    def setUp(self):
        usuario1 = Usuario.objects.create(first_name="Usuário 1", username="teste1")
        usuario2 = Usuario.objects.create(first_name="Usuário 2", username="teste2")
        usuario3 = Usuario.objects.create(first_name="Usuário 3", username="teste3")

        # Criando 3 disciplinas

        disciplina_matematica = Disciplina.objects.create(nome="Matemática")
        disciplina_portugues = Disciplina.objects.create(nome="Português")
        disciplina_historia = Disciplina.objects.create(nome="História")

        # Definindo interesse dos usuários

        usuario1.interesses.add(disciplina_matematica)
        usuario1.interesses.add(disciplina_historia)
        usuario2.interesses.add(disciplina_historia)

        # Criando 5 conteúdos

        cont_mat_1 = Conteudo.objects.create(nome="Números inteiros", disciplina = disciplina_matematica)
        cont_mat_2 = Conteudo.objects.create(nome="Números reais", disciplina = disciplina_matematica)
        cont_port_1 = Conteudo.objects.create(nome="Acentuação", disciplina = disciplina_portugues)
        cont_hist_1 = Conteudo.objects.create(nome="História do Brasil", disciplina = disciplina_historia)
        cont_hist_2 = Conteudo.objects.create(nome="História geral", disciplina = disciplina_historia)

        # Criando 3 planos de aula

        plano_aula_1 = PlanoAula.objects.create(
            responsavel=usuario1,
            titulo="Plano de aula 1",
            contextualizacao = "Como vai ser",
            descricao_atividade = "Como vai ser",
            robo_equipamento = "Aqui",
            robo_descricao = "Sim",
            prog_linguagem = "Python",
            prog_descricao = "nada a declarar"
        )
        plano_aula_2 = PlanoAula.objects.create(
            responsavel=usuario1,
            titulo="Plano de aula 2",
            contextualizacao = "Como vai ser",
            descricao_atividade = "Como vai ser",
            robo_equipamento = "Aqui",
            robo_descricao = "Sim",
            prog_linguagem = "Python",
            prog_descricao = "nada a declarar"
        )
        plano_aula_3 = PlanoAula.objects.create(
            responsavel=usuario2,
            titulo="Plano de aula 3",
            contextualizacao = "Como vai ser",
            descricao_atividade = "Como vai ser",
            robo_equipamento = "Aqui",
            robo_descricao = "Sim",
            prog_linguagem = "Python",
            prog_descricao = "nada a declarar"
        )
        plano_aula_4 = PlanoAula.objects.create(
            responsavel=usuario2,
            titulo="Plano de aula 4",
            contextualizacao = "Como vai ser",
            descricao_atividade = "Como vai ser",
            robo_equipamento = "Aqui",
            robo_descricao = "Sim",
            prog_linguagem = "Python",
            prog_descricao = "nada a declarar"
        )

        # Atribuindo conteúdos a planos de aula.
        # Conteúdo de Português não tem nenhum plano de aula associado a ele

        plano_aula_1.conteudos.add(cont_mat_1)
        plano_aula_1.conteudos.add(cont_mat_2)
        plano_aula_2.conteudos.add(cont_mat_2)
        plano_aula_2.conteudos.add(cont_hist_1)
        plano_aula_3.conteudos.add(cont_hist_1)
        plano_aula_3.conteudos.add(cont_hist_2)
        plano_aula_3.conteudos.add(cont_mat_1)
        plano_aula_3.conteudos.add(cont_mat_2)
        plano_aula_4.conteudos.add(cont_mat_1)

        # Likes e execuções em planos de aula

        LikePlanoAula.objects.create(usuario=usuario1, plano_aula=plano_aula_3)
        LikePlanoAula.objects.create(usuario=usuario2, plano_aula=plano_aula_1)
        # LikePlanoAula.objects.create(usuario=usuario3, plano_aula=plano_aula_3)

        ExecucaoPlanoAula.objects.create(usuario=usuario1, plano_aula=plano_aula_3)
        # ExecucaoPlanoAula.objects.create(usuario=usuario2, plano_aula=plano_aula_2)
        # ExecucaoPlanoAula.objects.create(usuario=usuario2, plano_aula=plano_aula_3)
        ExecucaoPlanoAula.objects.create(usuario=usuario2, plano_aula=plano_aula_1)
        ExecucaoPlanoAula.objects.create(usuario=usuario1, plano_aula=plano_aula_4)
    
    def test_disciplinas_interesse(self):
        usuario1 = Usuario.objects.get(first_name="Usuário 1")
        usuario2 = Usuario.objects.get(first_name="Usuário 2")
        usuario3 = Usuario.objects.get(first_name="Usuário 3")

        disciplina_matematica = Disciplina.objects.get(nome="Matemática")
        disciplina_portugues = Disciplina.objects.get(nome="Português")
        disciplina_historia = Disciplina.objects.get(nome="História")

        self.assertEqual(sc.disciplinas_interesse(usuario1.id, []), [disciplina_historia, disciplina_matematica])
        self.assertEqual(sc.disciplinas_interesse(usuario2.id, []), [disciplina_historia])
        self.assertEqual(sc.disciplinas_interesse(usuario3.id, []), [])
    
    def test_disciplinas_favoritadas(self):
        usuario1 = Usuario.objects.get(first_name="Usuário 1")
        usuario2 = Usuario.objects.get(first_name="Usuário 2")
        usuario3 = Usuario.objects.get(first_name="Usuário 3")

        disciplina_matematica = Disciplina.objects.get(nome="Matemática")
        disciplina_portugues = Disciplina.objects.get(nome="Português")
        disciplina_historia = Disciplina.objects.get(nome="História")

        self.assertEqual(sc.disciplinas_favoritadas(usuario1.id, []), [disciplina_historia, disciplina_matematica])
        self.assertEqual(sc.disciplinas_favoritadas(usuario2.id, []), [disciplina_matematica])
        self.assertEqual(sc.disciplinas_favoritadas(usuario3.id, []), [])

        self.assertEqual(sc.disciplinas_favoritadas(usuario1.id, sc.disciplinas_interesse(usuario1.id, [])),
                          [])
        self.assertEqual(sc.disciplinas_favoritadas(usuario2.id, sc.disciplinas_interesse(usuario2.id, [])),
                          [disciplina_matematica])
        self.assertEqual(sc.disciplinas_favoritadas(usuario3.id, sc.disciplinas_interesse(usuario3.id, [])),
                          [])

    def test_disciplinas_executadas(self):
        usuario1 = Usuario.objects.get(first_name="Usuário 1")
        usuario2 = Usuario.objects.get(first_name="Usuário 2")
        usuario3 = Usuario.objects.get(first_name="Usuário 3")

        disciplina_matematica = Disciplina.objects.get(nome="Matemática")
        disciplina_portugues = Disciplina.objects.get(nome="Português")
        disciplina_historia = Disciplina.objects.get(nome="História")

        self.assertEqual(sc.disciplinas_executadas(usuario1, []), [disciplina_historia, disciplina_matematica])
        self.assertEqual(sc.disciplinas_executadas(usuario2, []), [disciplina_matematica])
        self.assertEqual(sc.disciplinas_executadas(usuario3, []), [])

        self.assertEqual(sc.disciplinas_executadas(usuario1.id, sc.disciplinas_favoritadas(usuario1.id, sc.disciplinas_interesse(usuario1.id, [])) +
                                                    sc.disciplinas_interesse(usuario1.id, [])),
                          [])
        self.assertEqual(sc.disciplinas_executadas(usuario2.id, sc.disciplinas_favoritadas(usuario2.id, sc.disciplinas_interesse(usuario2.id, [])) +
                                                    sc.disciplinas_interesse(usuario2.id, [])),
                          [])
        self.assertEqual(sc.disciplinas_executadas(usuario3.id, sc.disciplinas_favoritadas(usuario3.id, sc.disciplinas_interesse(usuario3.id, [])) +
                                                    sc.disciplinas_interesse(usuario3.id, [])),
                          [])
    
    def test_todas_disciplinas(self):
        usuario1 = Usuario.objects.get(first_name="Usuário 1")
        usuario2 = Usuario.objects.get(first_name="Usuário 2")
        usuario3 = Usuario.objects.get(first_name="Usuário 3")

        disciplina_matematica = Disciplina.objects.get(nome="Matemática")
        disciplina_portugues = Disciplina.objects.get(nome="Português")
        disciplina_historia = Disciplina.objects.get(nome="História")

        self.assertEqual(sc.todas_disciplinas([]), 
                         [disciplina_historia, disciplina_matematica, disciplina_portugues]
                         )
        
        self.assertEqual(
            sc.todas_disciplinas(sc.disciplinas_interesse(usuario1.id, []) +
                                sc.disciplinas_favoritadas(usuario1.id, sc.disciplinas_interesse(usuario1.id, [])) +
                                sc.disciplinas_executadas(usuario1.id, sc.disciplinas_interesse(usuario1.id, []) + sc.disciplinas_favoritadas(usuario1.id, sc.disciplinas_interesse(usuario1.id, [])))),
            [disciplina_portugues]
        )
        
        self.assertEqual(
            sc.todas_disciplinas(sc.disciplinas_interesse(usuario2.id, []) +
                                sc.disciplinas_favoritadas(usuario2.id, sc.disciplinas_interesse(usuario2.id, [])) +
                                sc.disciplinas_executadas(usuario2.id, sc.disciplinas_interesse(usuario2.id, []) + sc.disciplinas_favoritadas(usuario2.id, sc.disciplinas_interesse(usuario2.id, [])))),
            [disciplina_portugues]
        )
        
        self.assertEqual(
            sc.todas_disciplinas(sc.disciplinas_interesse(usuario3.id, []) +
                                sc.disciplinas_favoritadas(usuario3.id, sc.disciplinas_interesse(usuario3.id, [])) +
                                sc.disciplinas_executadas(usuario3.id, sc.disciplinas_interesse(usuario3.id, []) + sc.disciplinas_favoritadas(usuario3.id, sc.disciplinas_interesse(usuario3.id, [])))),
            [disciplina_historia, disciplina_matematica, disciplina_portugues]
        )

    def test_ordenar(self):
        plano_aula_1 = PlanoAula.objects.get(titulo="Plano de aula 1")
        plano_aula_2 = PlanoAula.objects.get(titulo="Plano de aula 2")
        plano_aula_3 = PlanoAula.objects.get(titulo="Plano de aula 3")
        plano_aula_4 = PlanoAula.objects.get(titulo="Plano de aula 4")

        self.assertEqual(
            sc.ordenar([plano_aula_1, plano_aula_2, plano_aula_3, plano_aula_4]),
            [plano_aula_1, plano_aula_3, plano_aula_4, plano_aula_2]
        )

        self.assertEqual(
            sc.ordenar([plano_aula_1, plano_aula_2, plano_aula_4]),
            [plano_aula_1, plano_aula_4, plano_aula_2]
        )

    def test_encontrar_planos_aula_por_disciplina(self):
        disciplina_matematica = Disciplina.objects.get(nome="Matemática")
        disciplina_portugues = Disciplina.objects.get(nome="Português")
        disciplina_historia = Disciplina.objects.get(nome="História")

        lista_disciplinas_1 = [disciplina_matematica, disciplina_portugues, disciplina_historia]
        lista_disciplinas_2 = [disciplina_portugues, disciplina_historia]

        plano_aula_1 = PlanoAula.objects.get(titulo="Plano de aula 1")
        plano_aula_2 = PlanoAula.objects.get(titulo="Plano de aula 2")
        plano_aula_3 = PlanoAula.objects.get(titulo="Plano de aula 3")
        plano_aula_4 = PlanoAula.objects.get(titulo="Plano de aula 4")

        lista_planos_aula = PlanoAula.objects.all()

        self.assertEqual(
            sc.encontrar_planos_aula_por_disciplina(lista_disciplinas_1, 5, lista_planos_aula),
            [plano_aula_1, plano_aula_3, plano_aula_4, plano_aula_2]
        )

        self.assertEqual(
            sc.encontrar_planos_aula_por_disciplina(lista_disciplinas_1, 3, lista_planos_aula),
            [plano_aula_1, plano_aula_3, plano_aula_4]
        )

        self.assertEqual(
            sc.encontrar_planos_aula_por_disciplina(lista_disciplinas_2, 5, lista_planos_aula),
            [plano_aula_3, plano_aula_2]
        )

        self.assertEqual(
            sc.encontrar_planos_aula_por_disciplina(lista_disciplinas_2, 1, lista_planos_aula),
            [plano_aula_3]
        )

    def test_sugestao_planos_aula(self):
        usuario1 = Usuario.objects.get(first_name="Usuário 1")
        usuario2 = Usuario.objects.get(first_name="Usuário 2")
        usuario3 = Usuario.objects.get(first_name="Usuário 3")

        plano_aula_1 = PlanoAula.objects.get(titulo="Plano de aula 1")
        plano_aula_2 = PlanoAula.objects.get(titulo="Plano de aula 2")
        plano_aula_3 = PlanoAula.objects.get(titulo="Plano de aula 3")
        plano_aula_4 = PlanoAula.objects.get(titulo="Plano de aula 4")

        self.assertEqual(
            sc.sugestao_planos_aula(usuario1, 10),
            [plano_aula_3, plano_aula_4]
        )

        self.assertEqual(
            sc.sugestao_planos_aula(usuario2, 10),
            [plano_aula_2, plano_aula_1]
        )

        self.assertEqual(
            sc.sugestao_planos_aula(usuario2, 1),
            [plano_aula_2]
        )

        self.assertEqual(
            sc.sugestao_planos_aula(usuario3, 10),
            [plano_aula_1, plano_aula_3, plano_aula_4, plano_aula_2]
        )
    
    # def test_encontrar_planos_aula_disciplina(self):
    #     planos_aula = PlanoAula.objects.all()
    #     disciplinas = list(Disciplina.objects.filter(status='Ativo'))

    #     inf_disciplinas = planos_aula_views.encontrar_planos_aula_disciplina(planos_aula, disciplinas)

    #     self.assertEqual(inf_disciplinas[0][1], 2)
    #     self.assertEqual(inf_disciplinas[1][1], 3)
    #     self.assertEqual(inf_disciplinas[2][1], 0)
    
    # def test_likes_execucao_por_conteudo(self):
    #     planos_aula = PlanoAula.objects.all()
    #     conteudos = list(Conteudo.objects.filter(status='Ativo'))

    #     inf_conteudos = planos_aula_views.likes_execucao_por_conteudo(planos_aula, conteudos)

    #     self.assertEqual(inf_conteudos[0][1], 3)
    #     self.assertEqual(inf_conteudos[1][1], 2)
    #     self.assertEqual(inf_conteudos[2][1], 4)
    #     self.assertEqual(inf_conteudos[3][1], 5)
    #     self.assertEqual(inf_conteudos[4][1], 0)
    
    # def test_encontrar_principais_conteudos(self):
    #     planos_aula = PlanoAula.objects.all()
    #     conteudos = list(Conteudo.objects.filter(status='Ativo'))

    #     principais_conteudos = planos_aula_views.encontrar_principais_conteudos(planos_aula_views.likes_execucao_por_conteudo(planos_aula, conteudos), 3)

    #     # Os principais conteúdos são Matemática 2, Matemática 1 e História 1
    #     # Lembrando que like e execução em um plano de aula não conta como 2

    #     self.assertEqual(len(principais_conteudos),3)
    #     self.assertEqual(principais_conteudos[0][0].id,2)
    #     self.assertEqual(principais_conteudos[1][0].id,1)
    #     self.assertEqual(principais_conteudos[2][0].id,4)
    
    # def test_encontrar_principais_planos_aula(self):
    #     planos_aula = PlanoAula.objects.all()

    #     principais_planos_aula = planos_aula_views.encontrar_principais_planos_aula(planos_aula, 5)

    #     self.assertEqual(len(principais_planos_aula), 3)
    #     self.assertEqual(principais_planos_aula[0][0].id, 1)
    #     self.assertEqual(principais_planos_aula[1][0].id, 3)
    #     self.assertEqual(principais_planos_aula[2][0].id, 2)

    #     self.assertEqual(principais_planos_aula[0][1], 2)
    #     self.assertEqual(principais_planos_aula[1][1], 2)
    #     self.assertEqual(principais_planos_aula[2][1], 1)