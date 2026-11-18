# Fluxos de negócio

## Emissão e fila

1. A rota web `/filas/gerar/` emite senha normal; `/filas/preferencial/` emite preferencial. `FilaService.emitir_senha` valida o tipo e numera a sequência do dia por tipo.
2. A senha é criada com estado `espera`. A View apresenta `totem/senha_gerada.html`.
3. `FilaService.chamar_proxima` valida o guichê ativo, finaliza uma chamada anterior ainda marcada como `chamando` naquele guichê, escolhe uma senha do dia aguardando, associa-a ao guichê e registra `Historico`.
4. A regra implementada tenta uma preferencial quando o contador de chamadas satisfaz o ciclo de três chamadas; se o tipo esperado não estiver disponível, usa o outro tipo.
5. A rechamada registra `chamando_novamente` para a senha atual. A API também chama os mesmos services através de actions de `SenhaViewSet`.

## Atendimento

`AtendimentoService.iniciar_atendimento` valida o guichê e a senha, muda seu estado para `atendimento`, cria `Atendimento` com hora inicial e registra o histórico. Ao finalizar, o service grava `fim`, muda a senha para `finalizado` e registra a ação. Há também uma operação de transferência para outro guichê ativo, com registro de histórico.

## Estados modelados de Senha

Os choices do Model `filas.Senha` são `espera`, `chamando`, `chamando_novamente`, `atendimento` e `finalizado`. `chamando_novamente` é usado como ação histórica; o service de rechamada mantém o estado da senha como `chamando`. Não foi inferido estado de cancelamento.

## Canais

O fluxo web de totem e guichê usa Views Django e templates. A API REST da aplicação, montada em `/api/v1/`, oferece operações por DRF e encaminha emissão, chamada e operações de atendimento aos mesmos services. O painel de TV e métricas também têm rotas web e endpoints JSON conforme os arquivos de URL.
