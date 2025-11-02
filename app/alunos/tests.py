from datetime import date
from django.test import TestCase
from rest_framework import status
from transporte.models import Rota
from rest_framework.test import APIClient
from alunos.models import Encarregado, Aluno
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserModelTestCase(TestCase):
    def test_cria_usuario(self):
        user = User.objects.create_user(
            email="test@example.com",
            nome="Jo Salomao",
            role="ENCARREGADO",
            password="Senhacommais8"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("Senhacommais8"))
        self.assertEqual(user.role, "ENCARREGADO")
        self.assertTrue(user.is_active)


class EncarregadoModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="encarregado@email.com",
            nome="Ana Maria",
            role="ENCARREGADO",
            password="Senhacommais8"
        )

    def test_criar_encarregado(self):
        encarregado = Encarregado.objects.create(
            user=self.user,
            telefone="+258841064877",
            nrBI="6548757498E",
            endereco="Bairro Central, Q.1, N342"
        )
        encarregado.full_clean()
        self.assertEqual(encarregado.user.email, "encarregado@email.com")
        self.assertEqual(encarregado.telefone, "+258841064877")


class AlunoModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="encarregado@email.com",
            nome="Maria Rosa",
            role="ENCARREGADO",
            password="Senhacommais8"
        )
        self.encarregado = Encarregado.objects.create(
            user=self.user,
            telefone="841083315",
            nrBI="868468419P",
            endereco="bairro Central, Q.1, N42"
        )
        self.rota = Rota.objects.create(nome="Rota-A")

    def test_criar_aluno(self):
        aluno = Aluno.objects.create(
            nome="João Da Silva",
            data_nascimento=date(2017, 6, 15),
            nrBI="9876543218Y",
            encarregado=self.encarregado,
            escola_dest="Escola Primária Central",
            classe="3ª",
            rota=self.rota,
            activo=True,
            mensalidade="1500.00",
            email="joao.silva@gmail.com"
        )
        aluno.full_clean()
        self.assertEqual(aluno.nome, "João Da Silva")
        self.assertEqual(aluno.email, "joao.silva@gmail.com")
        self.assertEqual(aluno.rota.nome, "Rota-A")


class EncarregadoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user1@email.com",
            nome="Carlos Mateus",
            role="ENCARREGADO",
            password="123789687",
        )
        self.encarregado = Encarregado.objects.create(
            user=self.user,
            telefone="+258841083334",
            nrBI="6846816518484R",
            endereco="maxaquene Q32, N45"
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Segundo encarregado para testes de permissão
        self.other_user = User.objects.create_user(
            email="other@email.com",
            nome="Outro Encarregado",
            role="ENCARREGADO",
            password="senha123",
        )
        self.other_encarregado = Encarregado.objects.create(
            user=self.other_user,
            telefone="+258840000000",
            nrBI="1111111111111A",
        )

    def test_listar_encarregado_apenas_o_proprio(self):
        """Garante que um encarregado só pode listar a si mesmo."""
        response = self.client.get("/api/alunos/encarregados/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.encarregado.id)

    def test_encarregado_nao_pode_ver_outro_encarregado(self):
        """Garante que um encarregado não pode acessar os detalhes de outro."""
        url = f"/api/alunos/encarregados/{self.other_encarregado.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_encarregado_nao_pode_atualizar_outro_encarregado(self):
        """Garante que um encarregado não pode atualizar os dados de outro."""
        url = f"/api/alunos/encarregados/{self.other_encarregado.id}/"
        payload = {"endereco": "Endereço Atualizado"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_encarregado_nao_pode_deletar_outro_encarregado(self):
        """Garante que um encarregado não pode deletar outro."""
        url = f"/api/alunos/encarregados/{self.other_encarregado.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_listar_encarregado(self):
        response = self.client.get("/api/alunos/encarregados/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["telefone"], "+258841083334")

    def test_criar_encarregado(self):
        payload = {
            "user": {
                "email": "user2@email.com",
                "nome":"Sandra Santos",
                "role":"ENCARREGADO",
                "password": "987456987"
            },
             "telefone": "+258879698468",
             "nrBI": "1001078475794P",
             "endereco": "Magoanine Q2, N4"
        }
        # user2 = User.objects.create_user(
        #     email="user2@email.com",
        #     nome="Sandra Santos",
        #     role="ENCARREGADO",
        #     password="987456987"
        # )
        # payload = {
        #     "user": user2.id,
        #     # "nome": "sezaltino Andre", #querendo acrescentar mais ainda a fazer estudos
        #     "telefone": "+258879698468",
        #     "nrBI": "1001078475794P",
        #     "endereco": "Magoanine Q2, N4"
        # }
        response = self.client.post("/api/alunos/encarregados/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Encarregado.objects.count(), 2)


    def test_atualizar_encarregado(self):
        url = f"/api/alunos/encarregados/{self.encarregado.id}/"
        payload = {"endereco": "Bairro Novo, N.45"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.encarregado.refresh_from_db()
        self.assertEqual(self.encarregado.endereco, "Bairro Novo, N.45")

    def test_deletar_encarregado(self):
        url = f"/api/alunos/encarregados/{self.encarregado.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Encarregado.objects.count(), 0)


class AlunoAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user1@email.com",
            nome="Carlos de lina",
            role="ENCARREGADO",
            password="Senhacommais8",
        )
        self.encarregado = Encarregado.objects.create(
            user=self.user,
            telefone="+258879647812",
            nrBI="1001015479745Y",
            endereco="guava Q34 N34"
        )
        self.aluno = Aluno.objects.create(
            nome="Celeste Narciso",
            data_nascimento=date(2012, 3, 15),
            nrBI="100101014787694P",
            escola_dest="Escola Primario de Matola-Gare",
            classe="4",
            mensalidade=2500.00,
            email="celeste@email.com",
            encarregado=self.encarregado,
            rota=Rota.objects.create(nome="Rota Test")
        )
        # utenticacao JWT
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_listar_alunos(self):
        url = f"/api/alunos/encarregados/{self.encarregado.id}/alunos/"
        response =  self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_criar_aluno(self):
        url = f"/api/alunos/encarregados/{self.encarregado.id}/alunos/"
        payload = {
            "nome": "Ana julia",
            "data_nascimento": "2010-05-20",
            "nrBI": "10010101245875549O",
            "escola_dest": "Escola secundaria da matola",
            "classe": "11",
            "mensalidade": 2500.00,
            "email": "ana@email.com"
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Aluno.objects.filter(encarregado=self.encarregado).count(), 2)
        #  vali para test
        aluno = Aluno.objects.get(email="ana@email.com")
        self.assertEqual(aluno.nome, payload["nome"])
        self.assertEqual(aluno.nrBI, payload["nrBI"])
        self.assertEqual(aluno.classe, payload["classe"])
        self.assertEqual(str(aluno.data_nascimento), payload["data_nascimento"])

    def test_atualizar_aluno(self):
        url = f"/api/alunos/encarregados/{self.encarregado.id}/alunos/{self.aluno.id}/"
        payload = {"classe": "5A"}
        response = self.client.patch(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.aluno.refresh_from_db()
        self.assertEqual(self.aluno.classe, "5A")

    def test_deletar_aluno(self):
        url = f"/api/alunos/encarregados/{self.encarregado.id}/alunos/{self.aluno.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Aluno.objects.count(), 0)
