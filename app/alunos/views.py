from rest_framework import viewsets
from alunos.models import Aluno, Encarregado
from alunos.serializers import AlunoSerializer, EncarregadoSerializer


class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer


class EncarregadoViewSet(viewsets.ModelViewSet):
    queryset = Encarregado.objects.all()
    serializer_class = EncarregadoSerializer
