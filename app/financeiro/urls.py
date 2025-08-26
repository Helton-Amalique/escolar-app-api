from rest_framework.routers import DefaultRouter
from financeiro.views import PagamentoViewSet, AlertaEnviadoViewSet, SalarioViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'pagamento', PagamentoViewSet)
router.register(r'alerta-enviado', AlertaEnviadoViewSet)
router.register(r'salario', SalarioViewSet)
# urlpatterns = [ ("", include(router.urls)), ]
urlpatterns = router.urls
