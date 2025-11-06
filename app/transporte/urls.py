from rest_framework.routers import DefaultRouter
from django.urls import path, include
from transporte.views import MotoristaViewSet, VeiculoViewSet, RotaViewSet

router = DefaultRouter()
router.register(r'motoristas', MotoristaViewSet, basename='motorista')
router.register(r'veiculos', VeiculoViewSet, basename='veiculo')
router.register(r'rotas', RotaViewSet, basename='rota')

urlpatterns = [
    path('', include(router.urls)),
]
