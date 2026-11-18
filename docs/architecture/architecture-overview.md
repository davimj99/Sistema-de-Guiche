# Visão geral da arquitetura

O projeto é uma aplicação Python/Django organizada em apps. Django fornece o framework web e a organização MTV: Models descrevem persistência, Views processam requisições e Templates renderizam páginas. O Django REST Framework está instalado e integrado ao mesmo processo Django; serializers validam e representam dados da API, e views/viewsets implementam operações. Services existentes concentram regras reutilizáveis de fila e atendimento. URLs e routers publicam as rotas.

A configuração de `senha_system/settings.py` escolhe PostgreSQL por padrão por meio de `DB_ENGINE`; SQLite pode ser selecionado explicitamente ou para testes quando configurado. O frontend identificado no repositório usa templates Django e arquivos estáticos HTML, CSS e JavaScript.

## Arquitetura geral

O fluxo web e a API REST entram no mesmo Django e compartilham services, Models e banco. DRF não é um processo ou serviço independente.

```mermaid
flowchart LR
    U[Usuários] --> W[Interface Web: templates Django, HTML, CSS e JavaScript]
    W --> D[Django: URLs e Views]
    D --> S[Services quando aplicável]
    S --> M[Models Django]
    M --> DB[(PostgreSQL padrão)]
    C[Clientes API] --> DRF[Django REST Framework integrado ao Django]
    DRF --> SER[Serializers: validação e representação]
    SER --> V[Views e ViewSets]
    V --> S
```

**Legenda:** setas indicam requisições, chamadas internas ou persistência. O banco pode ser SQLite quando a configuração explicitamente seleciona esse backend.
