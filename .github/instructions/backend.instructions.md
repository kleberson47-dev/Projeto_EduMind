---
applyTo: "backend/**/*.py"
---

# Regras de Desenvolvimento — Backend

Regras de Desenvolvimento
REGRA DE OURO: Desenvolva seguindo esta ordem lógica. Antes de avançar, valide mentalmente e por meio das ferramentas disponíveis que a etapa atual está consistente. Não implemente todas as camadas simultaneamente. Não tente criar Models, Serializers e Views tudo de uma vez. Construa o fluxo como uma linha de montagem linear.

O Fluxo Obrigatório de Desenvolvimento (Passo a Passo)
Para cada nova funcionalidade, rota de API ou recurso que for criar no sistema, siga estritamente esta ordem:
[1. MODEL] ➡️ [2. SERIALIZER] ➡️ [3. VIEWS / VIEWSETS] ➡️ [4. URLS]

Passo 1: O Modelo (models.Model)
O Model é a fundação e a única fonte da verdade do banco de dados.

Padrão de Nomenclatura: Nomes de classes sempre no singular e usando PascalCase (ex: DocumentoLicitatorio, TermoReferencia).

Campos de Auditoria: Todos os modelos principais devem conter campos de rastreabilidade:
criado_em = models.DateTimeField(auto_now_add=True)
atualizado_em = models.DateTimeField(auto_now=True)

Relacionamentos: Sempre defina explicitamente o comportamento de remoção (on_delete). Para dados públicos, governamentais ou críticos, priorize models.PROTECT. Use models.CASCADE apenas quando a dependência for estrita.

Validação de Integridade: Regras de negócio rígidas e invariáveis do dado (ex: formato de CNPJ, regras cadastrais) devem ser validadas no método clean() do próprio model.

Nota operacional: Rode as migrations (makemigrations/migrate) imediatamente após concluir este passo.

Passo 2: A Camada de Tradução (serializers)
O Serializer dita como o React consome os dados (JSON) e como o Django valida o que o Front-end envia.

Herança Correta: Use serializers.ModelSerializer para mapear modelos diretos. Use serializers.Serializer apenas para payloads customizados sem persistência direta em tabela (ex: requisições de disparo de relatórios).

Campos Explícitos: PROIBIDO o uso de fields = '__all__'. Defina explicitamente quais campos a API vai expor:
class ExemploSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exemplo
        fields = ['id', 'titulo', 'descricao', 'criado_em']
        read_only_fields = ['id', 'criado_em']
Validação de Entrada (validate_<campo>): Validações de formato e consistência dos dados vindos do formulário do Front-end devem ser tratadas aqui de forma isolada.

Passo 3: O Controlador da API (views / viewsets)
Orquestração de requisições utilizando o poder de abstração do Django REST Framework.

Prioridade para ModelViewSet: Se a rota precisar de um CRUD completo, use viewsets.ModelViewSet para garantir padronização RESTful nativa.

Isolamento de Lógica: A View serve apenas para receber, direcionar e responder à requisição. Regras de negócio complexas e pesadas devem ser isoladas em camadas de serviço (services.py) ou métodos auxiliares.

Paginação e Filtros: Toda View que lista dados (list) deve possuir paginação padrão e filtros explícitos utilizando django-filter para evitar sobrecarga no banco de dados.

Permissões Transparentes: Nunca omita permissões. Defina explicitamente quem tem acesso:
from rest_framework.permissions import IsAuthenticated
permission_classes = [IsAuthenticated]

Passo 4: As Rotas (urls.py)
Para ModelViewSet, utilize obrigatoriamente o DefaultRouter do DRF para registrar o endpoint.

Todas as rotas de API do sistema devem possuir o prefixo e versionamento estrito: api/v1/.

Práticas Proibidas (Checklist Antierro)
[ ] Tratamento de exceção genérico: Não use except Exception:. Trate os erros conhecidos e esperados da aplicação de forma cirúrgica (ex: ObjectDoesNotExist, ValidationError).

[ ] Gargalo N+1 no Serializer: Não faça consultas de banco dentro de loops ou propriedades do serializer. Resolva relacionamentos direto na View correspondente utilizando select_related ou prefetch_related no get_queryset().

[ ] Exposição de Segredos: Chaves de API, credenciais externas e a SECRET_KEY do Django devem residir unicamente no arquivo .env, mapeadas através de pacotes como python-dotenv ou decouple.