from rest_framework import viewsets
from alunos.models import Encarregado, Aluno
from alunos.serializers import EncarregadoSerializer, AlunoSerializer
from alunos.permissions import IsAdminOrOwner


class EncarregadoViewSet(viewsets.ModelViewSet):
    queryset = Encarregado.objects.all()
    serializer_class = EncarregadoSerializer
    permission_classes = [IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Encarregado.objects.all()
        if hasattr(user, 'perfil_encarregado'):
            return Encarregado.objects.filter(user=user)
        return Encarregado.objects.none()  # Retorna queryset vazio se não for admin nem encarregado

class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer
    permission_classes = [IsAdminOrOwner]

    def get_queryset(self):
        user = self.request.user
        encarregado_pk = self.kwargs.get("encarregado_pk")

        if user.is_staff:
            if encarregado_pk:
                return Aluno.objects.filter(encarregado_id=encarregado_pk)
            return Aluno.objects.all()

        if hasattr(user, 'perfil_encarregado'):
            encarregado = user.perfil_encarregado
            if encarregado_pk and str(encarregado.pk) != encarregado_pk:
                 return Aluno.objects.none()  # Encarregado tentando acessar alunos de outro encarregado
            return Aluno.objects.filter(encarregado=encarregado)
        
        return Aluno.objects.none() # Retorna queryset vazio por padrão

    def perform_create(self, serializer):
        user = self.request.user
        encarregado_pk = self.kwargs.get("encarregado_pk")

        # Apenas admin pode criar para qualquer encarregado
        if user.is_staff and encarregado_pk:
            serializer.save(encarregado_id=encarregado_pk)
        # Encarregado só pode criar para si mesmo
        elif hasattr(user, 'perfil_encarregado') and str(user.perfil_encarregado.pk) == encarregado_pk:
            serializer.save(encarregado=user.perfil_encarregado)
        else:
            # Impede a criação se as condições não forem atendidas
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Você não tem permissão para criar um aluno para este encarregado.")
