/**
 * index.js - Controle de Tema (Dark/Light) e Idiomas (PT/EN)
 * Portal e Vitrine Comercial
 */

(function () {
    "use strict";

    /* ========================================================
       DICIONÁRIO DE TRADUÇÕES (PT / EN)
       ======================================================== */
    const translations = {
        pt: {
            "nav_modules": "Módulos",
            "nav_solutions": "Para Empresas & Clientes",
            "nav_tv": "Painel TV",
            "nav_totem": "Totem",
            "status_online": "ONLINE",
            "admin_link": "🔒 Admin",

            "hero_badge": "⚡ Versão 1.9 • Pronto para Produção",
            "hero_title": "Gestão Inteligente de Filas, Atendimento e Operações",
            "hero_desc": "Controle em tempo real de filas com alternância prioritária por lei, painéis multimídia interativos com veiculação de anúncios, gestão de EPIs e portal de solicitações.",
            "hero_btn_totem": "🎫 Abrir Totem de Senhas",
            "hero_btn_tv": "📺 Abrir Painel TV de Chamadas",
            "hero_btn_solutions": "💼 Conhecer Solução para Novos Clientes",

            "section_modules_title": "📁 Módulos da Plataforma",
            "section_modules_desc": "Acesse rapidamente as ferramentas operacionais ativas na sua instituição ou empresa.",

            "card1_tag": "Tempo Real",
            "card1_title": "Totem de Senhas",
            "card1_desc": "Interface de autoatendimento para retirada de senhas convencionais e preferenciais com geração automática de tickets.",
            "card1_btn": "Acessar Totem",
            "card1_sub_normal": "Emitir Senha Normal",
            "card1_sub_pref": "Emitir Preferencial",

            "card2_tag": "Multimídia",
            "card2_title": "Painel de TV Institucional",
            "card2_desc": "Exibição visual das chamadas com áudio integrado, histórico de atendimentos e carrossel de propagandas e comunicados em vídeo/imagem.",
            "card2_btn": "Abrir Painel TV Fullscreen",
            "card2_sub_simple": "Painel Web Simples",

            "card3_tag": "Operador",
            "card3_title": "Guichê de Atendimento",
            "card3_desc": "Controle de atendimento pelo operador: chamar próxima senha (com alternância inteligente prioritária), repetir chamada e encerrar.",
            "card3_label_station": "Selecione sua estação de trabalho:",
            "card3_btn": "Acessar Guichê Principal",

            "card4_tag": "Segurança do Trabalho",
            "card4_title": "Controle de EPIs",
            "card4_desc": "Gestão de Equipamentos de Proteção Individual: controle de estoque mínimo, registro de entrega para colaboradores e prazos de troca.",
            "card4_btn": "Painel de EPIs",
            "card4_sub_deliveries": "Entregas",
            "card4_sub_stock": "Estoque",
            "card4_sub_employees": "Funcionários",

            "card5_tag": "Autoatendimento",
            "card5_title": "Portal de Acesso Wi-Fi",
            "card5_desc": "Formulário simplificado para solicitação de acesso à rede sem fio institucional com emissão de protocolo e acompanhamento.",
            "card5_btn": "Solicitar Acesso",
            "card5_sub_track": "Consultar Protocolo",

            "card6_tag": "Gestão & BI",
            "card6_title": "Relatórios de Atendimento",
            "card6_desc": "Estatísticas consolidadas de atendimentos, métricas por atendente, classificação por tipo de demanda e exportação de relatórios em PDF.",
            "card6_btn": "Ver Relatórios",
            "card6_sub_pdf": "Gerar PDF",

            "showcase_title": "💼 Solução Corporativa para Futuros Clientes",
            "showcase_sub": "Construído para atender faculdades, redes de ensino, clínicas, laboratórios, cartórios e centrais de atendimento que buscam modernização, controle rigoroso e alta confiabilidade operacional.",

            "feat1_title": "Alternância Legal de Prioridades",
            "feat1_desc": "Algoritmo de balanceamento de senhas que garante o atendimento prioritário legal (idosos, gestantes, PCD) sem sobrecarregar a fila convencional.",

            "feat2_title": "Painel Multimídia Publicitário",
            "feat2_desc": "Monetize ou divulgue comunicados: reprodução de vídeos em alta definição e banners rotativos enquanto o público aguarda a chamada.",

            "feat3_title": "Controle Concorrente Confiável",
            "feat3_desc": "Arquitetura com travas atômicas no banco de dados contra chamadas duplicadas e perda de integridade em múltiplos guichês simultâneos.",

            "feat4_title": "Modular e Personalizável",
            "feat4_desc": "Adapte os módulos à sua necessidade: ative apenas filas, adicione segurança do trabalho (EPIs), cadastros ou solicitação de serviços internos.",

            "feat5_title": "Implantação Rápida em Nuvem",
            "feat5_desc": "Empacotado com Docker, Nginx e PostgreSQL. Fácil de escalar, criar backups automáticos e hospedar em qualquer provedor de nuvem.",

            "feat6_title": "Auditoria e Relatórios Executivos",
            "feat6_desc": "Gere relatórios oficiais em PDF com tempos de atendimento, guichês mais demandados e histórico detalhado para compliance.",

            "cta_title": "Interessado em levar esta plataforma para a sua organização?",
            "cta_desc": "Oferecemos modelos flexíveis de implantação com personalização completa de marca e módulos.",
            "cta_whatsapp": "💬 WhatsApp Comercial",
            "cta_email": "✉️ Falar por E-mail",

            "whatsapp_tooltip": "Fale Conosco no WhatsApp",
            "footer_rights": "Plataforma de Atendimento e Gestão Integrada • Faculdade ISCON",
            "footer_tech": "Desenvolvido com Python & Django • Release v1.9"
        },

        en: {
            "nav_modules": "Modules",
            "nav_solutions": "For Businesses & Clients",
            "nav_tv": "TV Display",
            "nav_totem": "Kiosk",
            "status_online": "ONLINE",
            "admin_link": "🔒 Admin",

            "hero_badge": "⚡ Version 1.9 • Production Ready",
            "hero_title": "Smart Queue Management, Customer Service & Operations",
            "hero_desc": "Real-time queue control with regulatory priority alternation, interactive multimedia displays with ads, PPE supply management, and digital requests portal.",
            "hero_btn_totem": "🎫 Open Ticket Kiosk",
            "hero_btn_tv": "📺 Open TV Calling Display",
            "hero_btn_solutions": "💼 Explore Enterprise Solutions",

            "section_modules_title": "📁 Platform Modules",
            "section_modules_desc": "Quickly access operational tools active in your institution or company.",

            "card1_tag": "Real-Time",
            "card1_title": "Ticket Kiosk",
            "card1_desc": "Self-service interface for generating standard and priority tickets with automatic sequence management.",
            "card1_btn": "Launch Kiosk",
            "card1_sub_normal": "Issue Regular Ticket",
            "card1_sub_pref": "Issue Priority Ticket",

            "card2_tag": "Multimedia",
            "card2_title": "TV Calling Display Board",
            "card2_desc": "Visual queue display with voice/audio alerts, recent ticket history, and video/image digital signage announcements.",
            "card2_btn": "Open Fullscreen TV Board",
            "card2_sub_simple": "Simple Web Board",

            "card3_tag": "Operator",
            "card3_title": "Service Desk",
            "card3_desc": "Agent interface: call next ticket (with priority alternation), recall ticket, and manage active service sessions.",
            "card3_label_station": "Select your desk station:",
            "card3_btn": "Access Main Desk",

            "card4_tag": "Work Safety",
            "card4_title": "PPE Management (EPI)",
            "card4_desc": "Personal Protective Equipment control: minimum stock monitoring, employee delivery logging, and renewal deadlines.",
            "card4_btn": "PPE Dashboard",
            "card4_sub_deliveries": "Deliveries",
            "card4_sub_stock": "Inventory",
            "card4_sub_employees": "Employees",

            "card5_tag": "Self-Service",
            "card5_title": "Wi-Fi Access Portal",
            "card5_desc": "Streamlined portal for student/user institutional wireless network requests with real-time protocol tracking.",
            "card5_btn": "Request Access",
            "card5_sub_track": "Track Protocol",

            "card6_tag": "Management & BI",
            "card6_title": "Service Reports",
            "card6_desc": "Consolidated service analytics, metrics per agent, demand category breakdowns, and official PDF exports.",
            "card6_btn": "View Reports",
            "card6_sub_pdf": "Generate PDF",

            "showcase_title": "💼 Enterprise Solution for Future Clients",
            "showcase_sub": "Built for universities, schools, medical clinics, laboratories, legal offices, and customer service centers seeking modernization and high operational reliability.",

            "feat1_title": "Regulatory Priority Alternation",
            "feat1_desc": "Smart queue balancing algorithm ensuring statutory priority service without bottlenecking standard customers.",

            "feat2_title": "Multimedia Advertising Display",
            "feat2_desc": "Monetize or inform: broadcast high-definition videos and rotating ad banners while users wait for service.",

            "feat3_title": "Atomic Concurrency Control",
            "feat3_desc": "Database architecture with atomic row-level locks preventing duplicate ticket calls across multiple simultaneous desks.",

            "feat4_title": "Modular & Highly Customizable",
            "feat4_desc": "Tailor modules to your business: activate only queues, add safety equipment (PPE), registration forms, or helpdesk.",

            "feat5_title": "Rapid Cloud & Docker Deployment",
            "feat5_desc": "Containerized with Docker, Nginx, and PostgreSQL. Easy to scale, automate backups, and host on any cloud provider.",

            "feat6_title": "Auditing & Executive Reports",
            "feat6_desc": "Export official PDF reports detailing wait times, desk loads, and full transaction history for compliance.",

            "cta_title": "Interested in deploying this platform for your organization?",
            "cta_desc": "We provide flexible deployment models with full custom branding and module adaptation.",
            "cta_whatsapp": "💬 Commercial WhatsApp",
            "cta_email": "✉️ Email Our Team",

            "whatsapp_tooltip": "Chat with Us on WhatsApp",
            "footer_rights": "Integrated Service & Management Platform • ISCON",
            "footer_tech": "Engineered with Python & Django • Release v1.9"
        }
    };

    /* ========================================================
       GERENCIAMENTO DE TEMA (DARK / LIGHT)
       ======================================================== */
    const themeToggleBtn = document.getElementById("themeToggle");
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const storedTheme = localStorage.getItem("site-theme");
    const initialTheme = storedTheme || (prefersDark ? "dark" : "light");

    function applyTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("site-theme", theme);

        if (themeToggleBtn) {
            themeToggleBtn.innerHTML = theme === "dark" ? "☀️" : "🌙";
            themeToggleBtn.setAttribute(
                "title",
                theme === "dark" ? "Alternar para Modo Claro" : "Alternar para Modo Escuro"
            );
            themeToggleBtn.setAttribute(
                "aria-label",
                theme === "dark" ? "Alternar para Modo Claro" : "Alternar para Modo Escuro"
            );
        }
    }

    applyTheme(initialTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", function () {
            const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            applyTheme(newTheme);
        });
    }

    /* ========================================================
       GERENCIAMENTO DE IDIOMA (PT / EN)
       ======================================================== */
    const storedLang = localStorage.getItem("site-lang") || "pt";

    function applyLanguage(lang) {
        const selectedLang = translations[lang] ? lang : "pt";
        const dict = translations[selectedLang];

        document.documentElement.lang = selectedLang === "pt" ? "pt-BR" : "en";
        localStorage.setItem("site-lang", selectedLang);

        // Atualiza textos marcados com data-i18n
        document.querySelectorAll("[data-i18n]").forEach(function (el) {
            const key = el.getAttribute("data-i18n");
            if (dict[key]) {
                el.textContent = dict[key];
            }
        });

        // Atualiza botões do seletor
        document.querySelectorAll(".core-lang-btn").forEach(function (btn) {
            if (btn.getAttribute("data-lang") === selectedLang) {
                btn.classList.add("active");
                btn.setAttribute("aria-pressed", "true");
            } else {
                btn.classList.remove("active");
                btn.setAttribute("aria-pressed", "false");
            }
        });
    }

    applyLanguage(storedLang);

    document.querySelectorAll(".core-lang-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            const lang = this.getAttribute("data-lang");
            applyLanguage(lang);
        });
    });

})();
