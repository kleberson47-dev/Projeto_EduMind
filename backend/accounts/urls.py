from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import CustomTokenObtainPairSerializer
from .views.user_viewset import UsuarioViewSet
from .views.auth_views import CustomTokenObtainPairView

router = DefaultRouter()
router.register(r"accounts", UsuarioViewSet, basename="accounts")

urlpatterns = [
    path("accounts/token/", CustomTokenObtainPairView.as_view(), name="token_obtain"),
    path("accounts/token/refresh/",
         TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
