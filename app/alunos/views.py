from rest_framework import viewsets
from alunos.models import Encarregado, Aluno
from rest_framework.exceptions import PermissionDenied
from alunos.serializers import EncarregadoSerializer, AlunoSerializer
from .permissions import IsAdminOrOwner


class EncarregadoViewSet(viewsets.ModelViewSet):
    queryset = Encarregado.objects.select_related('user').prefetch_related('alunos').all()
    serializer_class = EncarregadoSerializer
    permission_classes = [IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
            # return Encarregado.objects.all()
        if hasattr(user, 'perfil_encarregado'):
            return self.queryset.filter(user=user)
            # return Encarregado.objects.filter(user=user)
        return Encarregado.objects.none()


class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.select_related('encarregado__user', 'rota__veiculo').all()
    serializer_class = AlunoSerializer
    permission_classes = [IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        encarregado_pk = self.request.query_params.get('encarregado_pk')

        if user.is_staff:
            # encarregado_pk = self.kwargs.get("encarregado_pk")
            if encarregado_pk:
                return self.queryset.filter(encarregado_id=encarregado_pk)
            # return self.queryset
            # return Aluno.objects.all()

        if hasattr(user, 'perfil_encarregado'):
            return self.queryset.filter(encarregado_id=encarregado_pk)
            # return Aluno.objects.filter(encarregado=user.perfil_encarregado)

        return Aluno.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        encarregado_pk = self.request.query_params.get('encarregado_pk')
        # encarregado_pk = self.kwargs.get("encarregado_pk")

        # Apenas admin pode criar para qualquer encarregado
        if user.is_staff and encarregado_pk:
            serializer.save(encarregado_id=encarregado_pk)
        # Encarregado só pode criar para si mesmo
        elif hasattr(user, 'perfil_encarregado') and str(user.perfil_encarregado.pk) == encarregado_pk:
            serializer.save(encarregado=user.perfil_encarregado)
        else:
            # Impede a criação se as condições não forem atendidas
            raise PermissionDenied("Você não tem permissão para criar um aluno para este encarregado.")
