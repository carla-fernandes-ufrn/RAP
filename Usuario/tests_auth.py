from datetime import timedelta

from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from Usuario.models import CodigoValidacao, Usuario


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="Projeto RAP Testes <testes@rap.invalid>",
    SECRET_KEY="segredo-exclusivo-dos-testes-que-nunca-deve-ser-enviado",
)
class AuthenticationCriticalTests(TestCase):
    password = "Senha-Forte-2026!"

    def create_user(self, username=None, email=None, **kwargs):
        serial = Usuario.objects.count() + 1
        username = username or f"aluno{serial}"
        email = email or f"aluno{serial}@example.com"
        return Usuario.objects.create_user(
            username=username,
            email=email,
            password=self.password,
            first_name="Pessoa",
            last_name="Teste",
            cidade="Natal",
            estado="RN",
            **kwargs,
        )

    def registration_data(self, **overrides):
        data = {
            "username": "novoaluno",
            "email": "NovoAluno@Example.com",
            "password1": "Cadastro-Seguro-2026!",
            "password2": "Cadastro-Seguro-2026!",
        }
        data.update(overrides)
        return data

    def messages(self, response):
        return [str(message) for message in get_messages(response.wsgi_request)]

    # Login e autorizacao
    def test_login_com_senha_correta(self):
        user = self.create_user()
        response = self.client.post(
            reverse("usuario:login"),
            {"username": user.username, "password": self.password},
        )
        self.assertRedirects(response, reverse("home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_login_recusa_senha_incorreta(self):
        user = self.create_user()
        response = self.client.post(
            reverse("usuario:login"),
            {"username": user.username, "password": "senha-incorreta"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_recusa_usuario_inexistente(self):
        response = self.client.post(
            reverse("usuario:login"),
            {"username": "nao-existe", "password": self.password},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_recusa_usuario_inativo(self):
        user = self.create_user()
        user.is_active = False
        user.save(update_fields=["is_active"])
        response = self.client.post(
            reverse("usuario:login"),
            {"username": user.username, "password": self.password},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_area_protegida_exige_login(self):
        protected_url = reverse("disciplina:listar")
        response = self.client.get(protected_url)
        self.assertRedirects(
            response,
            f'{reverse("usuario:login")}?next={protected_url}',
        )

    def test_todos_os_tipos_autenticados_acessam_area_comum(self):
        for index, tipo in enumerate(("Aluno", "Professor", "Administrador", "Root")):
            with self.subTest(tipo=tipo):
                user = self.create_user(
                    username=f"usuario{index}",
                    email=f"usuario{index}@example.com",
                    tipo_usuario=tipo,
                )
                self.client.force_login(user)
                self.assertEqual(
                    self.client.get(reverse("disciplina:listar")).status_code,
                    200,
                )
                self.client.logout()

    def test_area_administrativa_diferencia_tipos(self):
        url = reverse("usuario:listar_ativos")
        aluno = self.create_user(tipo_usuario="Aluno")
        self.client.force_login(aluno)
        self.assertEqual(self.client.get(url).status_code, 403)

        admin = self.create_user(
            username="admin", email="admin@example.com", tipo_usuario="Administrador"
        )
        self.client.force_login(admin)
        self.assertEqual(self.client.get(url).url.split("?")[0], reverse("usuario:validar_admin"))

        root = self.create_user(
            username="root", email="root@example.com", tipo_usuario="Root"
        )
        self.client.force_login(root)
        self.assertEqual(self.client.get(url).status_code, 200)

    # Cadastro, e-mail e confirmacao
    def test_cadastro_valido_cria_usuario_inativo_codigo_e_email(self):
        raw_password = self.registration_data()["password1"]
        response = self.client.post(reverse("usuario:cadastrar"), self.registration_data())
        self.assertRedirects(response, reverse("usuario:ativar_email"))

        user = Usuario.objects.get(username="novoaluno")
        self.assertFalse(user.is_active)
        self.assertEqual(user.email, "novoaluno@example.com")
        self.assertEqual(user.tipo_usuario, "Aluno")
        self.assertTrue(user.check_password(raw_password))

        code = CodigoValidacao.objects.get(usuario=user, tipo="CADASTRO")
        self.assertRegex(code.codigo, r"^\d{6}$")
        self.assertFalse(code.utilizado)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [user.email])
        self.assertEqual(email.subject, "Confirmação de Cadastro - RAP")
        self.assertIn(code.codigo, email.body)
        self.assertIn(code.codigo, email.alternatives[0].content)
        self.assertNotIn(raw_password, email.body)
        self.assertNotIn(raw_password, email.alternatives[0].content)
        self.assertNotIn("segredo-exclusivo-dos-testes", email.body)
        self.assertNotIn("segredo-exclusivo-dos-testes", email.alternatives[0].content)

    def test_fluxo_integrado_cadastro_email_e_ativacao(self):
        self.client.post(reverse("usuario:cadastrar"), self.registration_data())
        user = Usuario.objects.get(username="novoaluno")
        validation = CodigoValidacao.objects.get(usuario=user, tipo="CADASTRO")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(validation.codigo, mail.outbox[0].body)

        response = self.client.post(
            reverse("usuario:ativar_email"), {"codigo": validation.codigo}
        )
        self.assertRedirects(response, reverse("usuario:login"))
        user.refresh_from_db()
        validation.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(validation.utilizado)

    def test_reenvio_de_cadastro_invalida_codigo_anterior(self):
        self.client.post(reverse("usuario:cadastrar"), self.registration_data())
        user = Usuario.objects.get(username="novoaluno")
        old_code = CodigoValidacao.objects.get(usuario=user, tipo="CADASTRO")
        mail.outbox.clear()

        response = self.client.post(
            reverse("usuario:ativar_email"), {"acao": "reenviar"}
        )
        self.assertRedirects(response, reverse("usuario:ativar_email"))
        old_code.refresh_from_db()
        new_code = CodigoValidacao.objects.get(
            usuario=user, tipo="CADASTRO", utilizado=False
        )
        self.assertTrue(old_code.utilizado)
        self.assertNotEqual(old_code.pk, new_code.pk)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(new_code.codigo, mail.outbox[0].body)

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.dummy.EmailBackend"
    )
    def test_falha_smtp_mantem_usuario_inativo_e_remove_codigo_nao_entregue(self):
        from unittest.mock import patch

        with patch("Usuario.views.send_mail", side_effect=OSError("SMTP indisponível")):
            response = self.client.post(
                reverse("usuario:cadastrar"), self.registration_data()
            )

        self.assertRedirects(response, reverse("usuario:ativar_email"))
        user = Usuario.objects.get(username="novoaluno")
        self.assertFalse(user.is_active)
        self.assertFalse(
            CodigoValidacao.objects.filter(usuario=user, tipo="CADASTRO").exists()
        )
        self.assertTrue(
            any("Não foi possível enviar o código" in message for message in self.messages(response))
        )

    def test_cadastro_valida_campos_obrigatorios_e_email(self):
        for field, value in (("username", ""), ("email", ""), ("password1", ""), ("email", "invalido")):
            with self.subTest(field=field, value=value):
                data = self.registration_data(**{field: value})
                if field == "password1":
                    data["password2"] = ""
                response = self.client.post(reverse("usuario:cadastrar"), data)
                self.assertEqual(response.status_code, 200)
                self.assertFormError(response.context["form"], field, response.context["form"].errors[field])
                self.assertEqual(Usuario.objects.count(), 0)

    def test_cadastro_recusa_username_e_email_duplicados(self):
        self.create_user(username="existente", email="existente@example.com")
        cases = (
            {"username": "existente"},
            {"email": "EXISTENTE@example.com"},
        )
        for override in cases:
            with self.subTest(override=override):
                response = self.client.post(
                    reverse("usuario:cadastrar"), self.registration_data(**override)
                )
                self.assertEqual(response.status_code, 200)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def make_activation(self, *, code="123456", age_minutes=0, used=False):
        user = self.create_user()
        user.is_active = False
        user.save(update_fields=["is_active"])
        validation = CodigoValidacao.objects.create(
            usuario=user, codigo=code, tipo="CADASTRO", utilizado=used
        )
        if age_minutes:
            CodigoValidacao.objects.filter(pk=validation.pk).update(
                criado_em=timezone.now() - timedelta(minutes=age_minutes)
            )
            validation.refresh_from_db()
        session = self.client.session
        session["ativacao_user_id"] = user.pk
        session.save()
        return user, validation

    def test_confirmacao_valida_ativa_usuario_e_invalida_reuso(self):
        user, validation = self.make_activation()
        response = self.client.post(reverse("usuario:ativar_email"), {"codigo": validation.codigo})
        self.assertRedirects(response, reverse("usuario:login"))
        user.refresh_from_db()
        validation.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(validation.utilizado)
        self.assertNotIn("ativacao_user_id", self.client.session)

        session = self.client.session
        session["ativacao_user_id"] = user.pk
        session.save()
        response = self.client.post(reverse("usuario:ativar_email"), {"codigo": validation.codigo})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("inválido" in message for message in self.messages(response)))

    def test_confirmacao_recusa_codigo_invalido_usado_expirado_e_de_outro_usuario(self):
        cases = (("invalido", {}), ("utilizado", {"used": True}), ("expirado", {"age_minutes": 16}))
        for name, kwargs in cases:
            with self.subTest(name=name):
                self.client = self.client_class()
                user, validation = self.make_activation(**kwargs)
                submitted = "000000" if name == "invalido" else validation.codigo
                self.assertEqual(
                    self.client.post(reverse("usuario:ativar_email"), {"codigo": submitted}).status_code,
                    200,
                )
                user.refresh_from_db()
                self.assertFalse(user.is_active)

        self.client = self.client_class()
        user, _ = self.make_activation(code="111111")
        other = self.create_user(username="outro", email="outro@example.com")
        CodigoValidacao.objects.create(usuario=other, codigo="222222", tipo="CADASTRO")
        response = self.client.post(reverse("usuario:ativar_email"), {"codigo": "222222"})
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    # Recuperacao de senha
    def request_recovery(self, email):
        return self.client.post(reverse("usuario:password_reset"), {"email": email})

    def test_recuperacao_existente_gera_codigo_e_email_sem_segredos(self):
        user = self.create_user()
        response = self.request_recovery(user.email)
        self.assertRedirects(response, reverse("usuario:validar_recuperacao"))
        code = CodigoValidacao.objects.get(usuario=user, tipo="RECUPERACAO")
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, [user.email])
        self.assertEqual(email.subject, "Recuperação de Senha - RAP")
        self.assertIn(code.codigo, email.body)
        self.assertIn(code.codigo, email.alternatives[0].content)
        self.assertNotIn(self.password, email.body)
        self.assertNotIn("segredo-exclusivo-dos-testes", email.body)
        self.assertNotIn("segredo-exclusivo-dos-testes", email.alternatives[0].content)

    def test_recuperacao_nao_enumera_email(self):
        user = self.create_user()
        existing = self.request_recovery(user.email)
        existing_messages = self.messages(existing)

        self.client = self.client_class()
        mail.outbox.clear()
        missing = self.request_recovery("ausente@example.com")
        missing_messages = self.messages(missing)

        self.assertEqual(existing.status_code, missing.status_code)
        self.assertEqual(existing.url, missing.url)
        self.assertEqual(existing_messages, missing_messages)
        self.assertEqual(len(mail.outbox), 0)

        missing_page = self.client.get(reverse("usuario:validar_recuperacao"))
        self.assertEqual(missing_page.status_code, 200)
        self.assertNotContains(missing_page, "ausente@example.com")

        missing_code = self.client.post(
            reverse("usuario:validar_recuperacao"), {"codigo": "123456"}
        )
        self.assertEqual(missing_code.status_code, 200)
        self.assertNotIn("redefinir_autorizado", self.client.session)

    def make_recovery(self, *, code="654321", age_minutes=0, used=False):
        user = self.create_user()
        validation = CodigoValidacao.objects.create(
            usuario=user, codigo=code, tipo="RECUPERACAO", utilizado=used
        )
        if age_minutes:
            CodigoValidacao.objects.filter(pk=validation.pk).update(
                criado_em=timezone.now() - timedelta(minutes=age_minutes)
            )
            validation.refresh_from_db()
        session = self.client.session
        session["recuperacao_user_id"] = user.pk
        session["recuperacao_solicitada"] = True
        session.save()
        return user, validation

    def test_fluxo_completo_altera_senha_e_codigo_nao_reutiliza(self):
        user = self.create_user()
        self.request_recovery(user.email)
        validation = CodigoValidacao.objects.get(usuario=user, tipo="RECUPERACAO")
        response = self.client.post(
            reverse("usuario:validar_recuperacao"), {"codigo": validation.codigo}
        )
        self.assertRedirects(response, reverse("usuario:redefinir_senha"))
        validation.refresh_from_db()
        self.assertTrue(validation.utilizado)

        new_password = "Nova-Senha-2026!"
        response = self.client.post(
            reverse("usuario:redefinir_senha"),
            {"new_password1": new_password, "new_password2": new_password},
        )
        self.assertRedirects(response, reverse("usuario:login"))
        self.assertFalse(self.client.login(username=user.username, password=self.password))
        self.assertTrue(self.client.login(username=user.username, password=new_password))

        self.client.logout()
        session = self.client.session
        session["recuperacao_user_id"] = user.pk
        session["recuperacao_solicitada"] = True
        session.save()
        response = self.client.post(
            reverse("usuario:validar_recuperacao"), {"codigo": validation.codigo}
        )
        self.assertEqual(response.status_code, 200)

    def test_recuperacao_recusa_codigo_invalido_usado_expirado_e_de_outro_usuario(self):
        cases = (("invalido", {}), ("utilizado", {"used": True}), ("expirado", {"age_minutes": 16}))
        for name, kwargs in cases:
            with self.subTest(name=name):
                self.client = self.client_class()
                _, validation = self.make_recovery(**kwargs)
                submitted = "000000" if name == "invalido" else validation.codigo
                response = self.client.post(
                    reverse("usuario:validar_recuperacao"), {"codigo": submitted}
                )
                self.assertEqual(response.status_code, 200)
                self.assertNotIn("redefinir_autorizado", self.client.session)

        self.client = self.client_class()
        _, _ = self.make_recovery(code="111111")
        other = self.create_user(username="outro", email="outro@example.com")
        CodigoValidacao.objects.create(usuario=other, codigo="222222", tipo="RECUPERACAO")
        response = self.client.post(
            reverse("usuario:validar_recuperacao"), {"codigo": "222222"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("redefinir_autorizado", self.client.session)
