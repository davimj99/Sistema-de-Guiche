# 🎫 Sistema de Gestão de Senhas e Atendimentos

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

Este é um sistema robusto desenvolvido em **Django** para a gestão de filas, chamadas de senhas e monitorização de atendimentos em tempo real.

## 📂 Estrutura do Projeto

O projeto está organizado nos seguintes módulos:

- **`accounts/`**: Gestão de utilizadores, autenticação e permissões de acesso.
- **`api/`**: Endpoints REST para integração com painéis externos ou aplicações mobile.
- **`atendimentos/`**: Registo e histórico de interações com os clientes.
- **`filas/`**: Lógica de organização de prioridades e fluxo de espera.
- **`frontend/`**: Assets (CSS/JS) e templates personalizados da interface.
- **`painel/`**: Interface visual otimizada para televisores ou monitores de sala de espera.
- **`core/`**: Configurações centrais do Django (settings, urls).

## 🛠 Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Framework Web:** Django
* **API:** Django REST Framework (DRF)
* **Base de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Produção)

* ⚙️ Funcionalidades Planeadas / Implementadas
[x] Autenticação e Níveis de Acesso.
[x] Geração de Senhas (Normal e Prioritária).
[x] Painel Visual de Chamada (TV).
[x] API REST para integração.
[ ] Relatórios de tempo médio de atendimento.
* **Frontend:** HTML5, CSS3 (Bootstrap)

