import re

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, UserRole


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        **TokenObtainPairSerializer.default_error_messages,
        "no_active_account": "E-mail ou senha inválidos.",
    }


class UserSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(
        write_only=True, required=False, source="password")

    class Meta:
        model = User
        fields = [
            "id",
            "nome",
            "email",
            "senha",
            "role",
            "avatar",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_role(self, value):
        valid_roles = {choice[0] for choice in UserRole.choices}
        if value not in valid_roles:
            raise serializers.ValidationError("Role invalida.")
        return value

    def validate_email(self, value):
        email = value.strip().lower()
        query = User.objects.filter(email=email)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("Email ja cadastrado.")
        return email

    def validate_nome(self, value):
        nome = value.strip()
        query = User.objects.filter(nome=nome)
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise serializers.ValidationError("Nome ja cadastrado.")
        return nome

    def validate_senha(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Senha deve ter no minimo 8 caracteres."
            )

        rules = [
            r"[A-Z]",
            r"[a-z]",
            r"[0-9]",
            r"[^A-Za-z0-9]",
        ]
        if not all(re.search(rule, value) for rule in rules):
            raise serializers.ValidationError(
                "Senha deve ter maiuscula, minuscula, numero e caractere especial."
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            raise serializers.ValidationError(
                {"senha": "Este campo e obrigatorio."}
            )
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
