from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response

from ..filters import ActivityFilter, MaterialFilter, ModuleFilter
from ..models import Activity, Classroom, ClassroomMaterial, Module
from ..pagination import PaginacaoPadrao
from ..serializers.activity_serializers import ActivitySerializer
from ..serializers.material_serializers import ClassroomMaterialSerializer
from ..serializers.module_serializers import (
    DefinirModoDistribuicaoSerializer,
    ModuleSerializer,
)
from ..services_atividades import (
    desativar_modulo,
    desativar_ou_excluir_atividade,
    publicar_atividade,
)
from ..services_notas import anotar_pesos_distribuidos, definir_modo_distribuicao


def _resposta_de_regra(exc):
    return Response(
        {"detail": " ".join(exc.messages)},
        status=status.HTTP_400_BAD_REQUEST,
    )


# Garante que o usuário é o professor dono da turma da URL e injeta a turma no contexto do serializer.
class TurmaDoProfessorMixin:
    @cached_property
    def turma(self):
        usuario = self.request.user
        if getattr(usuario, "role", None) != "professor":
            raise PermissionDenied(
                "Apenas professores podem gerenciar módulos, atividades e materiais.")

        turma = Classroom.objects.filter(
            id=self.kwargs.get("id"),
            professor=usuario,
        ).first()
        if turma is None:
            raise NotFound("Turma não encontrada ou não pertence ao professor.")
        return turma

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["turma"] = self.turma
        return context


# Lista e cria módulos de uma turma do professor logado.
class ProfessorClassroomModuleListCreateView(TurmaDoProfessorMixin, generics.ListCreateAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaginacaoPadrao
    filter_backends = [DjangoFilterBackend]
    filterset_class = ModuleFilter

    def get_queryset(self):
        return anotar_pesos_distribuidos(
            Module.objects.filter(turma=self.turma)
        ).order_by("ordem", "created_at")


# Detalha, renomeia e desativa um módulo da turma do professor.
class ProfessorClassroomModuleDetailView(TurmaDoProfessorMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "module_id"

    def get_queryset(self):
        return anotar_pesos_distribuidos(Module.objects.filter(turma=self.turma))

    def destroy(self, request, *args, **kwargs):
        modulo = self.get_object()
        try:
            desativar_modulo(modulo)
        except ValidationError as exc:
            return _resposta_de_regra(exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


# Define uma única vez o critério de distribuição de pontos do módulo.
class ProfessorClassroomModuleDistributionView(TurmaDoProfessorMixin, generics.GenericAPIView):
    serializer_class = DefinirModoDistribuicaoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        modulo = generics.get_object_or_404(
            Module,
            pk=kwargs.get("module_id"),
            turma=self.turma,
        )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            modulo = definir_modo_distribuicao(
                modulo, serializer.validated_data["modo"])
        except ValidationError as exc:
            return _resposta_de_regra(exc)

        return Response(
            ModuleSerializer(modulo, context=self.get_serializer_context()).data
        )


# Lista e cria atividades de uma turma pertencente ao professor logado.
class ProfessorClassroomActivityListCreateView(TurmaDoProfessorMixin, generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaginacaoPadrao
    filter_backends = [DjangoFilterBackend]
    filterset_class = ActivityFilter

    def get_queryset(self):
        return Activity.objects.filter(
            turma=self.turma,
        ).order_by("data_entrega", "-created_at")


# Detalha, atualiza e remove (ou desativa, se houver notas) uma atividade do professor.
class ProfessorClassroomActivityDetailView(TurmaDoProfessorMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "activity_id"

    def get_queryset(self):
        return Activity.objects.filter(turma=self.turma)

    def destroy(self, request, *args, **kwargs):
        atividade = self.get_object()
        resultado = desativar_ou_excluir_atividade(atividade)

        if resultado == "excluida":
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {
                "detail": "A atividade possui notas e foi apenas desativada.",
                "resultado": resultado,
            },
            status=status.HTTP_200_OK,
        )


# Publica uma atividade para que os alunos passem a visualizá-la.
class ProfessorClassroomActivityPublishView(TurmaDoProfessorMixin, generics.GenericAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        atividade = generics.get_object_or_404(
            Activity.objects.select_related("modulo"),
            pk=kwargs.get("activity_id"),
            turma=self.turma,
        )

        try:
            atividade = publicar_atividade(atividade)
        except ValidationError as exc:
            return _resposta_de_regra(exc)

        return Response(self.get_serializer(atividade).data)


# Lista e cadastra materiais complementares de uma turma do professor.
class ProfessorClassroomMaterialListCreateView(TurmaDoProfessorMixin, generics.ListCreateAPIView):
    serializer_class = ClassroomMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PaginacaoPadrao
    filter_backends = [DjangoFilterBackend]
    filterset_class = MaterialFilter

    def get_queryset(self):
        return ClassroomMaterial.objects.filter(turma=self.turma).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(turma=self.turma)


# Detalha, atualiza e remove um material complementar, apagando também o arquivo substituído ou removido.
class ProfessorClassroomMaterialDetailView(TurmaDoProfessorMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassroomMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "material_id"

    def get_queryset(self):
        return ClassroomMaterial.objects.filter(turma=self.turma)

    def perform_update(self, serializer):
        arquivo_antigo = (
            serializer.instance.arquivo.name
            if "arquivo" in serializer.validated_data
            else None
        )
        material = serializer.save()

        if arquivo_antigo and arquivo_antigo != material.arquivo.name:
            material.arquivo.storage.delete(arquivo_antigo)

    def perform_destroy(self, instance):
        arquivo = instance.arquivo
        instance.delete()
        arquivo.delete(save=False)