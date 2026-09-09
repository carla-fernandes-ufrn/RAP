from django.test import TestCase
from django.urls import reverse

from Usuario.models import Usuario


class PerfilSecurityTests(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="aluno",
            email="aluno@example.com",
            password="uma-senha-forte-123",
            first_name="Aluno",
            last_name="Teste",
            estado="RN",
            cidade="Natal",
            tipo_usuario="Aluno",
        )
        self.client.force_login(self.user)

    def test_usuario_nao_pode_promover_o_proprio_perfil(self):
        response = self.client.post(
            reverse("usuario:perfil"),
            {
                "form_tipo": "perfil",
                "username": "aluno",
                "email": "aluno@example.com",
                "first_name": "Aluno",
                "last_name": "Teste",
                "estado": "RN",
                "cidade": "Natal",
                "tipo_usuario": "Root",
            },
            secure=True,
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.tipo_usuario, "Aluno")

    def test_alteracao_ajax_de_senha_exige_login(self):
        self.client.logout()
        response = self.client.post(reverse("usuario:alterar_senha_ajax"), secure=True)
        self.assertEqual(response.status_code, 302)
