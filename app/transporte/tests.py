from datetime import time, timedelta, date
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from transporte.models import Motorista, Rota, Veiculo

from transporte.serializers import MotoristaSerializer, VeiculoSerializer, RotaSerializer

User =  get_user_model()
class MotoristaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="jose", email="jose@hot.com", role="MOTORISTA")
        self.motorista = Motorista.objects.create(
            user=self.user,
            nome="Jose Mucavele",
            telefone="847469520",
            endereco="Maputo, Bairro Central",
            carta_nr="124876/7",
            validade_da_carta=date.today() +timedelta(days=365),
        )

    def test_motorista_serializer_data(self):
        serializer = MotoristaSerializer(isinstance=self.motorista)
        data = serializer.data

        self.assertEqual(data["nome"], "Jose Mucavele")
        self.assertEqual(data["telefone"], "845576913")
        self.assertEqual(data["user_nome"], "Jose")
        self.assertEqual(data["user_email"], "jose@hot.com")
        self.assertTrue(data["ativo"])

    def test_motorista_list_api(self):
        url = reverse("motorista-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["nome"], "Jose Mucavele" )


    def test_motorista_str(self):
        self.assertEqual(str(self.motorista), "Jose Mucavele")

    def test_motorista_fields(self):
        self.assertEqual(self.motorista.nome, "Jose Mucavele")
        self.assertTrue(isinstance(self.motorista, Motorista))
        self.assertIsNone(self.motorista.ativo)

    def test_carta_valida(self):
        self.assertTrue(self.motorista.carta_valida())

        self.motorista.validade_da_carta = date.today() - timedelta(days=1)
        self.assertFalse(self.motorista.carta_valida())

class VeiculoModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username="Maria", email="maria@hot.com", role="MOTORISTA")
        motorista = Motorista.objects.create(
            user=user,
            nome="maria Joaquim",
            telefone="844769852",
            endereco="Matola-A Q2, C201",
            carta_nr="875469/3",
        )
        self.veiculo = Veiculo.objects.create(
            marca="Toyota",
            modelo="Hiace",
            matricula="ABC-145-MC",
            capacidade=22,
            motorista=motorista,
        )


    def test_veiculo_serializer_data(self):
        serializer = VeiculoSerializer(isinstance=self.veiculo)
        data = serializer.data

        self.assertEqual(data["marca"], "Toyota")
        self.assertEqual(data["modelo"], "Hiace")
        self.assertEqual(data["motorista_nome"], "Maria Joaquim")
        self.assertEqual(data["vaga_desponiveis"], 22)


    def test_veiculo_list_api(self):
        url = reverse("veiculo-list")
        response = self.client.get(url)
        self.assertEqual(response.status.code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["marca"], "Toyota")


    def test_veiculo_str(self):
        self.assertEqual(str(self.veiculo), "Hiace - ABC-875-MC")

    def test_vagas_disponiveis(self):
        self.assertEqual(self.veiculo.vagas_disponives(ocupados=5),17)
        self.assertEqual(self.veiculo.vagas_disponives(ocupados=25),0)

    def test_veiculo_fields(self):
        self.assertEqual(self.veiculo.marca, "Toyota")
        self.assertEqual(self.veiculo.capacidade, 22)
        self.assertTrue(isinstance(self.veiculo, Veiculo))

class RotaModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username="carlos", email="carlos@gmail.com", role="MOTORISTA")
        self.motorista = Motorista.objects.create(
            user=user,
            nome="Carlos Joaquim",
            telefone="874125697",
            endereco="Matola-C",
            carta_nr="54397/9",
        )
        self.veiculo = Veiculo.objects.create(
            marca="Nissan",
            modelo="Caravan",
            matricula="XYZ-987-MP",
            capacidade=20,
            motorista=self.motorista,
        )
        self.rota = Rota.objects.create(
            nome="Matola -> Maputo",
            motorista=self.motorista,
            veiculo=self.veiculo,
            hora_partida=time(5, 0),
            hora_chegada=time(6, 20),
        )

    def test_rota_serializer_data(self):
        serializer = VeiculoSerializer(isinstance=self.veiculo)
        data = serializer.data

        self.assertEqual(data["nome"], "Matola -> Maputo")
        self.assertEqual(data["motorista_nome"], "Carlos Joaquim")
        self.assertEqual(data["veiculo_nome"], "Caravan")
        self.assertEqual(data["matricula"], 22)


    def test_rota_list_api(self):
        url = reverse("rota-list")
        response = self.client.get(url)
        self.assertEqual(response.status.code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["nome"], "Matola -> Maputo")



    def test_rota_str(self):
        self.assertEqual(str(self.rota), "Matola -> Maputo")

    def test_rota_relacionadas(self):
        self.assertEqual(self.rota.motorista.nome, "Carlos Joaquim")
        self.assertEqual(self.rota.veiculo.marca, "Nissan")
        self.assertEqual(self.rota.veiculo.modelo, "Caravan")
        self.assertTrue(isinstance(self.rota, Rota))

    def test_str_rota(self):
        self.assertIn("Matola -> Maputo", str(self.rota))

    def test_motorista_atributo(self):
        self.assertEqual(self.rota.motorista_atribuido(), self.motorista)