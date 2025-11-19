from rest_framework.routers import DefaultRouter
from django.urls import path, include
from transporte.views import MotoristaViewSet, VeiculoViewSet, RotaViewSet, AlunoViewSet, EncarregadoViewSet

router = DefaultRouter()
router.register(r'motoristas', MotoristaViewSet, basename='motorista')
router.register(r'veiculos', VeiculoViewSet, basename='veiculo')
router.register(r'rotas', RotaViewSet, basename='rota')
router.register(r'alunos', AlunoViewSet, basename='aluno')
router.register(r'encarregados', EncarregadoViewSet, basename='encarregado')

urlpatterns = [
    path('', include(router.urls)),
]
