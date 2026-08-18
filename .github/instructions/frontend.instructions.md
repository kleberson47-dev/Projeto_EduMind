---
applyTo: "frontend/**/*.{ts,tsx,css}"
---

# Regras de Desenvolvimento — Frontend

## 1. Regra de Ouro

Mantenha o escopo isolado. Não crie múltiplos componentes, estados complexos e integrações globais de uma só vez.

Desenvolva em ciclos modulares: garanta que a tipagem e a estrutura do componente local estejam sólidas antes de conectá-lo a estados globais ou efeitos colaterais.


## 2. Fluxo Obrigatório de Desenvolvimento

Para cada nova tela, funcionalidade ou componente complexo, siga esta ordem lógica de construção:

```text
[1. TYPES] ➡️ [2. COMPONENT & PROPS] ➡️ [3. STATE & EVENTS] ➡️ [4. EFFECTS / HOOKS] ➡️ [5. GLOBAL STATE (REDUX)]
```

Antes de avançar para a próxima etapa, valide que a etapa atual está consistente, tipada e compatível com a arquitetura existente.

Não implemente múltiplas camadas simultaneamente sem necessidade.


## 3. Passo 1 — Tipagem Estrita

### Tipagem geral

Tudo no projeto deve ser tipado de forma explícita. Evite ao máximo o uso de comportamentos implícitos do JavaScript.

### Proibição de `any`

É proibido utilizar `any`.

Se um tipo for complexo ou desconhecido no momento:

* use `unknown`; ou
* crie uma interface ou tipo provisório apropriado.

Nunca utilize `any` apenas para contornar um erro de tipagem.

### `interface` e `type`

Prefira:

* `interface` para estruturas de objetos, como dados da API e Props;
* `type` para uniões, tipos primitivos combinados e outras composições apropriadas.

### Tipos provenientes do Backend

Os tipos TypeScript que representam entidades ou dados consumidos pelo frontend devem refletir o **contrato efetivamente exposto pela API**.

Quando houver diferença entre o Model do Django e o Serializer/API, considere o contrato da API como fonte de verdade para o tipo utilizado pelo frontend.

Exemplo:

```ts
interface Usuario {
  id: number;
  nome: string;
  email: string;
  criado_em: string;
}
```

Não adicione ao tipo frontend campos que o Serializer não disponibiliza apenas porque eles existem no Model do Django.


## 4. Passo 2 — Componentes, JSX e Props

Os componentes devem ser limpos, previsíveis e possuir responsabilidade única.

### Padrão de função

Use funções nomeadas tradicionais ou Arrow Functions de forma consistente com o padrão já existente no projeto.

O nome do arquivo e do componente deve utilizar PascalCase.

Exemplo:

```text
BotaoLicitacao.tsx
```

### Regras do JSX

Mantenha o JSX o mais limpo possível.

Evite:

* lógica complexa dentro do JSX;
* ternários triplos aninhados;
* processamento extenso diretamente dentro do `return`.

Se a lógica for longa, isole-a em uma função auxiliar ou variável antes do `return`.

### Renderização de listas

Sempre adicione uma `key` única e estável ao renderizar listas usando `.map()`.

Prefira identificadores estáveis vindos dos dados, como `id`.

Nunca utilize o índice do array (`index`) como `key`, exceto em situações absolutamente justificadas em que a lista seja estática e imutável.

### Tipagem de Props

Sempre declare explicitamente a interface das propriedades que o componente recebe.

Exemplo:

```tsx
interface BotaoProps {
  texto: string;
  onClick: (event: React.MouseEvent<HTMLButtonElement>) => void;
  desabilitado?: boolean;
}

export function BotaoLicitacao({
  texto,
  onClick,
  desabilitado = false,
}: BotaoProps) {
  return (
    <button onClick={onClick} disabled={desabilitado}>
      {texto}
    </button>
  );
}
```

## 5. Passo 3 — Estados Locais (`useState`) e Eventos

### Imutabilidade

Nunca altere um estado diretamente.

Errado:

```ts
usuario.nome = "João";
```

Use sempre a função modificadora:

```ts
setUsuario(...);
```

### Tipagem de estados

O TypeScript pode deduzir tipos simples.

Para objetos, arrays ou estados que começam como `null`, force a tipagem quando necessário.

Exemplo:

```ts
const [documento, setDocumento] = useState<Documento | null>(null);
const [listaErros, setListaErros] = useState<string[]>([]);
```

### Tipagem de eventos

Eventos de elementos HTML nativos devem ser tipados corretamente para garantir acesso seguro às propriedades de `event.target`.

Exemplo:

```ts
const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
  setBusca(event.target.value);
};
```

## 6. Passo 4 — Efeitos Colaterais (`useEffect`) e Custom Hooks

O `useEffect` deve ser utilizado exclusivamente para sincronizar o componente com sistemas externos.

Exemplos:

* chamadas de API;
* subscriptions;
* eventos externos;
* timers;
* integração com APIs do navegador;
* sincronização com sistemas externos.

Não utilize `useEffect` desnecessariamente para lógica que pode ser calculada diretamente durante a renderização ou através de funções/eventos.

### Array de dependências

Mantenha o array de dependências correto e completo.

Se o efeito depender de variáveis externas ao próprio efeito, essas dependências devem ser consideradas no array.

Se o efeito realmente deve executar apenas na montagem do componente, utilize `[]`, desde que o efeito não dependa de valores mutáveis externos que deveriam ser acompanhados.

### Função de limpeza

Sempre que o `useEffect` assinar um evento ou criar um recurso que precise ser encerrado, retorne uma função de limpeza.

Exemplos:

* `addEventListener`;
* `setInterval`;
* subscriptions;
* streams;
* listeners.

Isso evita vazamentos de memória (`memory leaks`).

### Custom Hooks

Se um componente começar a possuir muitos `useEffect` ou lógica complexa de estado, extraia essa lógica para um Custom Hook.

Exemplo:

```text
useLicitacoes.ts
```

O componente deve permanecer focado principalmente na renderização do JSX e na interação com o usuário.

## 7. Passo 5 — Estado Global (Redux Toolkit)

Use o estado global apenas para dados que precisam ser compartilhados por múltiplos componentes distantes na árvore.

Exemplos:

* dados do usuário logado;
* tema do sistema;
* permissões globais;
* estado de autenticação.

Se o dado pertence apenas a uma tela ou componente, prefira estado local com `useState`.

### Redux Toolkit

É obrigatório utilizar a estrutura moderna do Redux Toolkit (`createSlice`).

Não utilize o padrão antigo de Redux.

### Slices estruturados

Cada funcionalidade global deve possuir seu Slice contendo as actions e reducers relacionados àquela funcionalidade no mesmo arquivo, conforme o padrão adotado pelo projeto.

Exemplo:

```tsx
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
}

const initialState: AuthState = {
  token: null,
  isAuthenticated: false,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.token = null;
      state.isAuthenticated = false;
    },
  },
});

export const { setToken, logout } = authSlice.actions;
export default authSlice.reducer;
```

# 8. Organização de Arquivos e Reutilização

Para manter o projeto escalável, siga a estrutura de pastas abaixo:

```text
frontend/src/
├── components/       # Componentes visuais genéricos e reutilizáveis
├── features/         # Módulos específicos da aplicação
│   ├── components/   # Componentes usados apenas dentro desta feature
│   ├── authSlice.ts  # Estado global do Redux desta feature
│   └── hooks/        # Custom Hooks específicos desta feature
├── hooks/            # Custom Hooks globais
├── services/         # Configurações e chamadas para serviços externos/API
├── types/            # Definições de tipos globais TypeScript
└── utils/            # Funções puras de utilidade geral e formatação
```

## 9. Quando criar um arquivo em `utils/`

Crie um arquivo na pasta `utils/` apenas quando a função atender às condições abaixo.

### Função pura

A função:

* recebe uma entrada;
* processa os dados;
* retorna uma saída;
* não causa efeitos colaterais;
* não lê variáveis globais;
* não altera estados do React.

### Reutilização

A mesma lógica deve ter potencial real de reutilização em pelo menos dois lugares diferentes do sistema.

Exemplos:

* formatar uma data vinda do Django para `DD/MM/AAAA`;
* formatar uma string de CNPJ;
* validar ou transformar dados de maneira independente do React.

### Sem JSX

Arquivos de utilitários não devem conter JSX.

Utilize a extensão:

```text
.ts
```

e não:

```text
.tsx
```

# 10. Práticas Proibidas — Checklist Antierro

### Manipulação direta do DOM

Não manipule o DOM diretamente.

Evite comandos como:

```ts
document.getElementById(...)
```

Quando for necessário interagir diretamente com um elemento HTML, utilize as referências do React (`useRef`) ou a abordagem apropriada do React.

### Componentes gigantes

Não crie componentes gigantes.

Se o JSX de um arquivo ultrapassar aproximadamente 250 linhas, avalie a divisão do componente em subcomponentes menores e com responsabilidades bem definidas.

A divisão deve preservar a organização e não deve ser feita de forma artificial apenas para reduzir o número de linhas.

### Tratamento de erros de requisições

As chamadas de API devem utilizar a camada de `services/` e/ou a infraestrutura de requisições já existente no projeto.

O tratamento de erros deve ser centralizado sempre que a arquitetura existente permitir.

Não duplique desnecessariamente a mesma lógica de tratamento de erros em vários componentes.

Quando uma falha de requisição precisar ser comunicada ao usuário, forneça feedback visual adequado e compreensível.

# 11. Identidade Visual

O projeto deve seguir a mesma identidade visual da tela de login atual.

### Diretrizes visuais

* Fundo claro com tons de azul suave;
* Destaques em azul mais forte e ciano;
* Textos principais em azul escuro ou quase preto;
* Bordas leves;
* Cards com sombra suave;
* Visual limpo;
* Visual moderno;
* Visual consistente.

### Referência atual de cores

A tela de login atual deve ser utilizada como referência visual.

* Fundo geral: azul muito claro;
* Cor principal: azul forte;
* Cor de apoio: ciano / azul esverdeado;
* Texto: cinza azulado e azul escuro.

Ao criar novas telas, componentes ou elementos visuais, mantenha essa mesma linguagem visual para preservar a uniformidade do projeto.

Não altere a identidade visual existente sem necessidade ou solicitação.

# 12. Onde Cada Pasta Deve Ser Usada

## `src/content/pages/`

Aqui ficam as páginas completas da aplicação.

Use para:

* Login;
* Criar conta;
* Esqueceu senha;
* Dashboard;
* Listas de alunos;
* Listas de professores;
* Listas de turmas;
* Listas de tarefas;
* qualquer tela que ocupe a página inteira.

### Regra prática

Se for uma tela inteira, comece por aqui.

## `src/components/`

Aqui ficam componentes reutilizáveis e genéricos.

Use para:

* Botões;
* Inputs;
* Cards;
* Tabelas reutilizáveis;
* Loaders;
* Modais;
* componentes visuais que podem ser usados em mais de uma tela.

### Regra prática

Se o componente pode ser reaproveitado em várias páginas, ele fica aqui.

## `src/features/`

Aqui ficam módulos específicos de uma funcionalidade, como:

* Auth;
* Turmas;
* Alunos;
* Tarefas;
* Dashboard.

Use para:

* componentes específicos de uma feature;
* hooks específicos de uma feature;
* tipos específicos daquela área;
* lógica isolada por módulo.

Exemplo:

```text
features/auth/
```

para tudo que for relacionado à autenticação.

```text
features/alunos/
```

para funcionalidades específicas de alunos.

### Regra prática

Se a lógica pertence a uma única área do sistema, use `features/`.

## `src/layouts/`

Aqui ficam os layouts principais da aplicação.

Use para:

* Layout com sidebar;
* Layout base;
* Layout de autenticação;
* estruturas visuais que envolvem várias páginas.

### Regra prática

Se várias páginas compartilham a mesma moldura visual, essa estrutura deve ficar em `layouts/`.


## `src/middlewares/`

Aqui ficam proteções de rota e validações de acesso.

Use para:

* proteger páginas autenticadas;
* verificar permissões por role;
* bloquear acesso sem token.

### Regra prática

Se o objetivo é controlar quem pode entrar em uma rota, use essa pasta.

## `src/router.tsx`

Aqui ficam todas as rotas da aplicação.

Use para:

* criar novas rotas;
* organizar rotas públicas e privadas;
* registrar páginas com lazy loading;
* definir a navegação principal do app.

### Regra prática

Toda tela nova precisa ser registrada aqui.

## `src/services/`

Aqui ficam integrações com serviços externos e chamadas estruturadas.

Use para:

* Axios configurado;
* chamadas para API do backend;
* funções de autenticação;
* funções de comunicação com o servidor.

### Regra prática

Se uma função conversa com o backend, ela provavelmente deve ficar aqui.

## `src/utils/`

Aqui ficam funções puras e utilitários reutilizáveis.

Use para:

* formatação de data;
* funções de validação;
* constantes globais;
* URLs e caminhos de API;
* funções que não dependem do React.

### Regra prática

Se é uma função pura e reutilizável, use `utils/`.

## `src/types/`

Aqui ficam tipos globais do TypeScript.

Use para:

* tipos compartilhados entre várias partes do sistema;
* interfaces genéricas de API;
* tipos comuns entre páginas e serviços.

### Regra prática

Se o tipo será usado em mais de um lugar, considere colocá-lo em `types/`.

## `src/models/`

Aqui ficam os tipos ou estruturas que representam entidades do sistema.

Use para:

* Usuário;
* Turma;
* Tarefa;
* Permissão;
* dados de entidades da API que representam informações de negócio.

### Regra prática

Se o arquivo representa uma entidade de negócio, use `models/`.

## `src/utils/redux/`

Aqui fica a estrutura do estado global.

Use para:

* Store principal;
* Reducers;
* Slices;
* estado compartilhado da aplicação.

### Regra prática

Se os dados precisam ser usados por várias telas distantes, avalie o uso de Redux.

# 13. Caminho para Criar uma Nova Tela

Quando for criar uma tela nova, siga esta ordem:

1. Crie a página em `src/content/pages/`.
2. Se a página tiver partes reaproveitáveis, crie componentes em `src/components/` ou em `src/features/`.
3. Se precisar de tipos, coloque em `src/types/`, `src/models/` ou na estrutura específica da feature quando aplicável.
4. Se a tela consumir o backend, crie a função de serviço em `src/services/`.
5. Se precisar de alguma função auxiliar pura, use `src/utils/`.
6. Registre a rota em `src/router.tsx`.
7. Se a página precisar de proteção, aplique o middleware correspondente.
8. Mantenha a identidade visual existente do projeto.

### Exemplo prático

```text
Tela:
src/content/pages/NovaPagina.tsx

Componentes específicos:
src/features/nova-pagina/components/

Tipos específicos:
src/features/nova-pagina/types.ts

Chamadas API:
src/services/

Rota:
src/router.tsx
```

# 14. Caminho para Criar uma Nova Função

Se for uma nova função de negócio, siga este padrão:

1. Se a função for pura e reutilizável, coloque em `src/utils/`.
2. Se a função chamar API, coloque em `src/services/`.
3. Se a função pertencer a uma feature específica, coloque em `src/features/<feature>/`.
4. Se a função for usada globalmente e representar estado compartilhado, avalie Redux ou `src/utils/`, conforme sua responsabilidade.

Exemplos:

```text
Formatar data:
src/utils/formatDate.ts

Chamar login:
src/services/auth.ts

Gerar código de verificação:
src/features/auth/services/
```

# 15. Caminho para Criar um Novo Componente

1. Se for genérico e reutilizável, coloque em `src/components/`.
2. Se for exclusivo de uma feature, coloque em `src/features/<feature>/components/`.
3. Se fizer parte do layout geral, coloque em `src/layouts/`.

Exemplos:

```text
Tabela reutilizável:
src/components/

Cabeçalho exclusivo do dashboard:
src/layouts/

Formulário específico de autenticação:
src/features/auth/components/
```

# 16. Caminho para Alterar o Menu Lateral

Quando existir sidebar/menu:

1. O layout principal fica em `src/layouts/`.
2. Os itens de menu devem refletir as rotas registradas em `src/router.tsx`.
3. Se o item depender de permissões, use `src/middlewares/`.
4. Se o menu depender do perfil do usuário, os dados devem vir do estado global ou do endpoint do usuário logado.

### Regra prática

```text
Primeiro cria a rota
        ↓
Depois adiciona o item do menu
        ↓
Depois valida permissão e visibilidade
```

# 17. Caminho para Adicionar uma Nova Página Protegida

1. Criar a página em `src/content/pages/`.
2. Registrar a rota em `src/router.tsx`.
3. Envolver com `AuthMiddleware` ou `PermissionMiddleware`.
4. Usar o layout adequado em `src/layouts/`.
5. Consumir o backend através de `src/services/`.

# 18. Caminho para Manter o Projeto Consistente

* Sempre reutilize componentes antes de criar novos.
* Sempre coloque chamadas de API em `services/`.
* Sempre coloque funções puras em `utils/`.
* Sempre deixe as rotas centralizadas em `router.tsx`.
* Sempre mantenha o visual alinhado com a tela de login atual.
* Sempre prefira separar por feature quando a lógica crescer.
* Evite criar arquivos ou pastas sem necessidade.
* Antes de criar uma nova implementação, verifique se já existe uma solução reutilizável.
* Preserve a arquitetura existente.
* Não altere partes não relacionadas à tarefa solicitada.

# 19. Resumo Rápido

```text
Tela inteira:
src/content/pages/

Componente reutilizável:
src/components/

Parte específica de um módulo:
src/features/

Estrutura visual da página:
src/layouts/

Proteção de acesso:
src/middlewares/

Rotas:
src/router.tsx

API:
src/services/

Funções puras:
src/utils/

Tipos:
src/types/ e src/models/

Estado global:
src/utils/redux/
```

Este guia deve ser atualizado sempre que uma nova pasta, arquitetura ou padrão importante for criado no projeto.
