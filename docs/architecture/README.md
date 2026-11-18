# Documentação arquitetural

Documentação baseada no código e nas configurações em `senha_system/`.

| Documento | Conteúdo |
| --- | --- |
| [Visão geral](architecture-overview.md) | Django MTV, DRF e fluxos gerais |
| [Componentes](components.md) | Apps, responsabilidades e dependências |
| [Sequências](sequence-diagrams.md) | Emissão, fila, chamada e finalização |
| [Fluxos de negócio](business-flows.md) | Regras e estados do atendimento |
| [Modelo de dados](database-er.md) | Models e relacionamentos reais |
| [Implantação](deployment.md) | Topologia configurada em Docker Compose |

Os diagramas usam Mermaid. A implantação descrita corresponde aos arquivos de configuração versionados; ela não confirma que os contêineres estejam ativos em um ambiente específico.
