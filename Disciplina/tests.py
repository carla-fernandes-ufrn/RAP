from django.test import TestCase
from django.urls import reverse

from Disciplina.models import Disciplina
from Usuario.models import Usuario


class DisciplinaPermissionTests(TestCase):
    def test_usuario_comum_nao_pode_editar_disciplina(self):
        user = Usuario.objects.create_user(
            username="aluno", password="uma-senha-forte-123", tipo_usuario="Aluno"
        )
        disciplina = Disciplina.objects.create(nome="Matemática")
        self.client.force_login(user)

        response = self.client.post(
            reverse("disciplina:editar_disciplina", args=[disciplina.pk]),
            {"nome": "Nome adulterado"},
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        disciplina.refresh_from_db()
        self.assertEqual(disciplina.nome, "Matemática")
