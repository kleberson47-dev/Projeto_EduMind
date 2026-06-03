from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views.user_viewset import UsuarioViewSet

router = DefaultRouter()
router.register(r"accounts", UsuarioViewSet, basename="accounts")

urlpatterns = [
    path("accounts/token/", TokenObtainPairView.as_view(), name="token_obtain"),
    path("accounts/token/refresh/",
         TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]
