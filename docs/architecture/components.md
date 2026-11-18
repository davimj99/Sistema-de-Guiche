# Componentes Django

Os apps abaixo constam em `INSTALLED_APPS` ou no roteamento raiz. A API é parte do projeto Django e compartilha o domínio e a persistência.

## Dependências e comunicação

```mermaid
flowchart TB
    Browser[Navegador: templates e estáticos] --> Core[core: página inicial]
    Browser --> Accounts[accounts: autenticação e Guiche]
    Browser --> Filas[filas: totem, guichê, painel e fila]
    Browser --> Atendimento[atendimentos: relatórios e atendimento]
    Browser --> Painel[painel: painel público]
    Browser --> Epis[epis: funcionários, estoque e entregas]
    Browser --> Wifi[wifi: solicitações e acessos]
    Browser --> Dashboard[dashboard: métricas e monitoramento]
    Client[Cliente REST] --> API[api: DRF, serializers, ViewSets e routers]
    API --> FilaService[FilaService]
    API --> AtendService[AtendimentoService]
    Filas --> FilaService
    Atendimento --> AtendService
    FilaService --> FilaModels[Models filas e accounts]
    AtendService --> DomainModels[Models atendimentos, filas e accounts]
    Epis --> EpisModels[Models epis]
    Wifi --> WifiModels[Models wifi]
    Dashboard --> DashModels[ApiRequestLog e consultas do domínio]
    FilaModels --> DB[(Banco configurado)]
    DomainModels --> DB
    EpisModels --> DB
    WifiModels --> DB
    DashModels --> DB
```

## Responsabilidades observadas

| App | Responsabilidade observada |
| --- | --- |
| `core` | Página inicial e rota raiz. |
| `accounts` | Login, contas e entidade `Guiche`. |
| `filas` | Emissão de senha, chamadas, painel e Models de fila; contém `FilaService` e validadores. |
| `atendimentos` | Registros e relatórios; `AtendimentoService` inicia, transfere e finaliza atendimentos. |
| `api` | Endpoints DRF, serializers, ViewSets, router, autenticação/permissões e filtros. Consome Models dos domínios. |
| `painel` | Página e dados do painel público. |
| `dashboard` | Views, services e Model de monitoramento de chamadas à API. |
| `epis` | Funcionários, EPIs, estoque, entregas e relatórios. |
| `wifi` | Solicitações e registros de acesso Wi-Fi. |
| `frontend` | Diretório compartilhado de templates e estáticos configurado em `settings.py`; não é app instalado. |

URLs raiz em `senha_system/urls.py` incluem apps web e `api/`. Os endpoints de recursos DRF são conectados por `api/urls.py` e `api/routers.py`. Services foram documentados somente onde há classes concretas no código.
