# 🎫 Sistema de Gestão de Senhas e Atendimentos

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-REST%20API-red?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

Sistema robusto desenvolvido em **Django** para gestão de filas, emissão e chamada de senhas e monitoramento de atendimentos em tempo real. A aplicação é modular, separa responsabilidades em `models/` e `views/` por app e já está preparada para **deploy com Docker + Nginx**.


## ⚙️ Funcionalidades

- [x] Autenticação e níveis de acesso
- [x] Geração de senhas (normal e prioritária)
- [x] Gestão de filas com regras de prioridade
- [x] Painel visual de chamada (TV / monitor de sala de espera)
- [x] Painel visual de retirada de senha (totem)
- [x] Registro e histórico de atendimentos
- [x] API REST para integração com painéis externos e apps mobile
- [x] Estrutura pronta para produção (Docker, Nginx, `docker-compose.prod.yml`)
- [x] Relatórios de tempo médio de atendimento
- [x] Relatórios de controle de EPIS
- [ ] Dashboard de métricas por guichê e por atendente

---

## 🛠 Tecnologias

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.x |
| Framework web | Django |
| API | Django REST Framework (DRF) / SpringBoot |
| Banco de dados | SQLite (desenvolvimento) / PostgreSQL (produção) |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap |
| Servidor web / proxy reverso | Nginx |
| Containerização | Docker e Docker Compose |
| CI / Automação | GitHub (`.github/`) |

---

### Responsabilidade de cada módulo

| Módulo | Responsabilidade |
| --- | --- |
| `accounts/` | Cadastro de usuários, login/logout, grupos e permissões de acesso. |
| `api/` | Serializers, viewsets e rotas REST para consumo externo. |
| `atendimentos/` | Registro dos atendimentos, status, horários e histórico por cliente. |
| `filas/` | Geração de senhas, regras de prioridade e ordem de chamada. |
| `epis/` | Gestão de EPIs. |
| `painel/` | Tela pública de chamadas, otimizada para TVs e monitores. |
| `wifi/` | Funcionalidades relacionadas ao acesso Wi-Fi. |
| `frontend/` | Templates base, componentes e assets estáticos compartilhados. |
| `senha_system/` | `settings`, `urls` do projeto Django. |
| `nginx/` | Arquivos de configuração do proxy reverso usados no deploy. |

---

**Benefícios:**

- Arquivos menores e mais fáceis de revisar.
- Menos conflitos de merge em trabalho em equipe.
- Cada módulo evolui de forma independente, com responsabilidade única.
- Facilita testes e a futura extração de serviços.

> 💡 Ao criar um novo model, lembre-se de exportá-lo no `models/__init__.py` para que o Django o detecte nas migrations.

---

**Checklist de produção:**

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` única, forte e fora do repositório
- [ ] `ALLOWED_HOSTS` configurado com o domínio/IP do servidor
- [ ] Banco **PostgreSQL** configurado (não usar SQLite)
- [ ] HTTPS habilitado no Nginx (certificado TLS)
- [ ] Rotina de backup do banco ativa
- [ ] `.env` com permissões restritas e nunca versionado

---

## 🔐 Variáveis de Ambiente

Todas as configurações sensíveis ficam no arquivo `.env` (nunca o envie ao Git). Use o `.env.example` como modelo. Exemplo de variáveis típicas:

| Variável | Descrição | Exemplo |
| --- | --- | --- |
| `SECRET_KEY` | Chave secreta do Django | `troque-por-uma-chave-forte` |
| `DEBUG` | Modo debug (use `False` em produção) | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula | `meusite.com,localhost` |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | Credenciais do banco | — |
| `DB_HOST` / `DB_PORT` | Endereço do banco | `db` / `5432` |

> ⚠️ A lista acima é ilustrativa. Consulte o `.env.example` para as variáveis realmente utilizadas pelo projeto.

---

## 💾 Backups

O diretório `backups/` armazena os dumps do banco de dados. Exemplo com PostgreSQL via Docker:

```bash
# Gerar backup
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U <DB_USER> <DB_NAME> > backups/backup_$(date +%F).sql

# Restaurar backup
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U <DB_USER> <DB_NAME> < backups/backup_AAAA-MM-DD.sql
```

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para mais informações.