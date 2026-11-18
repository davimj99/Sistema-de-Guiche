# Diagramas de sequência

Os cenários abaixo seguem os handlers web e services existentes. O caminho alternativo via API é indicado onde o código chama o mesmo service.

## Emissão de senha e entrada na fila

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuário
    participant URL as filas/urls.py
    participant View as filas.views.totem
    participant Service as FilaService
    participant Model as filas.models.Senha
    participant DB as Banco configurado
    U->>URL: Solicitação em /filas/gerar/ ou /filas/preferencial/
    URL->>View: gerar_senha(tipo)
    View->>Service: emitir_senha(tipo)
    Service->>Model: buscar última senha do dia e tipo
    Model->>DB: consulta transacional
    DB-->>Service: última senha ou vazio
    Service->>Model: criar senha com status espera
    Model->>DB: INSERT
    DB-->>Service: Senha persistida
    Service-->>View: Senha
    View-->>U: render totem/senha_gerada.html
```

## Chamada, atendimento e finalização

```mermaid
sequenceDiagram
    autonumber
    actor A as Atendente autenticado
    participant View as filas.views.guiche
    participant Fila as FilaService
    participant S as Model Senha
    participant G as Model Guiche
    participant H as Model Historico
    participant Atendimento as AtendimentoService
    participant AM as Model Atendimento
    participant DB as Banco configurado
    A->>View: POST chamar_proxima(guiche_id)
    View->>Fila: chamar_proxima(guiche_id)
    Fila->>G: validar guichê ativo
    Fila->>S: selecionar próxima senha em espera
    Fila->>S: status chamando e associar guichê
    Fila->>H: registrar ação chamando
    Fila->>DB: confirmar transação
    View-->>A: redirecionar tela do guichê
    A->>Atendimento: iniciar_atendimento(senha_id, guiche_id, ...)
    Atendimento->>S: validar e mudar status para atendimento
    Atendimento->>AM: criar registro com início
    Atendimento->>H: registrar ação atendimento
    Atendimento->>DB: confirmar transação
    A->>Atendimento: finalizar_atendimento(atendimento_id)
    Atendimento->>AM: gravar fim
    Atendimento->>S: status finalizado
    Atendimento->>H: registrar ação finalizado
    Atendimento->>DB: confirmar transação
```

**Legenda:** `DB` representa o backend selecionado na configuração. Cada service opera em transação atômica conforme o código.
