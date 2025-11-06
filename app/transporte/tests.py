from datetime import date, timedelta
from django.test import TestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from transporte.models import Motorista, Rota, Veiculo

User = get_user_model()


class MotoristaAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            email="admin@admin.com", nome="Admin", password="password"
        )
        cls.user = User.objects.create_user(
            email="motorista@email.com",
            nome="Jose Mucavele",
            role="MOTORISTA",
            password="password",
        )
        cls.motorista = Motorista.objects.create(
            user=cls.user,
            telefone="+258847469520",
            endereco="Maputo, Bairro Central",
            carta_nr="124876/7",
            validade_da_carta=date.today() + timedelta(days=365),
        )

    def setUp(self):
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_listar_motoristas(self):
        response = self.client.get("/api/transporte/motoristas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user_nome"], "Jose Mucavele")

    def test_detalhe_motorista(self):
        response = self.client.get(f"/api/transporte/motoristas/{self.motorista.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_nome"], "Jose Mucavele")

    def test_criar_motorista(self):
        new_user = User.objects.create_user(
            email="novo@email.com", nome="Novo Motorista", role="MOTORISTA", password="password"
        )
        payload = {
            "user": new_user.id,
            "telefone": "+258820000000",
            "carta_nr": "987654/1",
            "validade_da_carta": (date.today() + timedelta(days=365)).strftime("%Y-%m-%d"),
        }
        response = self.client.post("/api/transporte/motoristas/", payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Motorista.objects.count(), 2)

    def test_validade_carta_expirada(self):
        user = User.objects.create_user(email="test@test.com", nome="test", role="MOTORISTA", password="password")
        with self.assertRaises(Exception):
             Motorista.objects.create(
                user=user,
                telefone="+258841111111",
                carta_nr="123",
                validade_da_carta=date.today() - timedelta(days=1),
            )

    def test_str_motorista(self):
        self.assertEqual(str(self.motorista), "Jose Mucavele")


class VeiculoAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            email="admin@admin.com", nome="Admin", password="password"
        )
        user = User.objects.create_user(
            email="motorista@email.com",
            nome="Maria Joaquim",
            role="MOTORISTA",
            password="password",
        )
        motorista = Motorista.objects.create(
            user=user,
            telefone="+258844769852",
            carta_nr="875469/3",
            validade_da_carta=date.today() + timedelta(days=365),
        )
        cls.veiculo = Veiculo.objects.create(
            marca="Toyota",
            modelo="Hiace",
            matricula="ABC-145-MC",
            capacidade=22,
            motorista=motorista,
        )

    def setUp(self):
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_listar_veiculos(self):
        response = self.client.get("/api/transporte/veiculos/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["motorista_nome"], "Maria Joaquim")

    def test_str_veiculo(self):
        self.assertEqual(str(self.veiculo), "Hiace - ABC-145-MC")

    def test_vagas_disponiveis(self):
        self.assertEqual(self.veiculo.vagas_disponiveis, 22)


class RotaAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser(
            email="admin@admin.com", nome="Admin", password="password"
        )
        user = User.objects.create_user(
            email="carlos@email.com",
            nome="Carlos Joaquim",
            role="MOTORISTA",
            password="password",
        )
        motorista = Motorista.objects.create(
            user=user,
            telefone="+258874125697",
            carta_nr="54397/9",
            validade_da_carta=date.today() + timedelta(days=365),
        )
        veiculo = Veiculo.objects.create(
            marca="Nissan",
            modelo="Caravan",
            matricula="XYZ-987-MP",
            capacidade=20,
            motorista=motorista,
        )
        cls.rota = Rota.objects.create(
            nome="Matola -> Maputo",
            veiculo=veiculo,
        )

    def setUp(self):
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_listar_rotas(self):
        response = self.client.get("/api/transporte/rotas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["nome"], "Matola -> Maputo")

    def test_detalhe_rota(self):
        response = self.client.get(f"/api/transporte/rotas/{self.rota.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["motorista"]["user_nome"], "Carlos Joaquim")
        self.assertEqual(response.data["veiculo"]["modelo"], "Caravan")

    def test_str_rota(self):
        self.assertEqual(str(self.rota), "Matola -> Maputo")

    def test_rota_motorista_property(self):
        self.assertEqual(self.rota.motorista.user.nome, "Carlos Joaquim")
