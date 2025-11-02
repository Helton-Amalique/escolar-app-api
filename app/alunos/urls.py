from django.urls import path, include
from rest_framework_nested import routers
from .views import AlunoViewSet, EncarregadoViewSet

router = routers.DefaultRouter()
router.register(r'encarregados', EncarregadoViewSet, basename="encarregado")

encarregado_router = routers.NestedDefaultRouter(router, r'encarregados', lookup='encarregado')
encarregado_router.register(r'alunos', AlunoViewSet, basename='encarregado-alunos')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(encarregado_router.urls)),
]
