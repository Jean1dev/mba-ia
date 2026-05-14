# Desafio 3 — Skill de Refatoração Arquitetural (`/refactor-arch`)

Este desafio implementa uma **Claude Code Custom Skill** capaz de analisar projetos legados, gerar relatórios de auditoria e refatorar automaticamente para o padrão MVC.

---

## Estrutura do Desafio

```
desafios/desafio-3-skill-refactor-arch/
├── code-smells-project/          # Projeto 1 — E-commerce (Python/Flask + raw SQLite)
├── ecommerce-api-legacy/         # Projeto 2 — LMS (Node.js/Express + sqlite3)
├── task-manager-api/             # Projeto 3 — Task Manager (Python/Flask + SQLAlchemy)
├── reports/
│   ├── audit-project-1.md
│   ├── audit-project-2.md
│   └── audit-project-3.md
└── README.md
```

Cada projeto contém a skill em `.claude/skills/refactor-arch/`.

---

## A Skill `/refactor-arch`

### Como invocar

```
/refactor-arch
```

### Arquivos da skill (`.claude/skills/refactor-arch/`)

| Arquivo | Conteúdo |
|---------|----------|
| `SKILL.md` | Orquestrador das 3 fases — lido automaticamente pelo Claude Code |
| `01-project-analysis.md` | Heurísticas de detecção de stack, framework, DB e arquitetura |
| `02-antipatterns-catalog.md` | Catálogo de 20 anti-padrões com sintomas e nomes padronizados |
| `03-audit-report-template.md` | Formato exato do relatório de auditoria |
| `04-mvc-architecture-guidelines.md` | Estrutura de diretórios e regras por camada (Python e Node.js) |
| `05-refactoring-playbook.md` | 8 padrões de transformação com código before/after |

### Fases de execução

**Fase 1 — Análise do Projeto**
- Detecta linguagem, framework e banco de dados
- Classifica a arquitetura atual (Monolítica / Parcialmente organizada / MVC)
- Infere o domínio de negócio
- Exibe relatório de análise e aguarda confirmação para continuar

**Fase 2 — Auditoria de Anti-padrões**
- Varre o código em busca dos 20 anti-padrões catalogados
- Gera relatório estruturado com severidade (CRITICAL → LOW), arquivo:linha e descrição
- Salva o relatório em `reports/audit-<projeto>.md`
- **Pausa obrigatória** — aguarda o usuário digitar `y` para iniciar a refatoração

**Fase 3 — Refatoração Automática**
- Cria a estrutura MVC em `src/`
- Aplica os padrões de transformação necessários
- Valida que a aplicação sobe sem erros
- Nunca altera os arquivos originais sem confirmação

### Regras não-negociáveis

- Fases 1 e 2 são somente leitura — nenhum arquivo é modificado
- Fase 3 só inicia após confirmação explícita do usuário
- Credenciais nunca são movidas para um local menos seguro
- Testes existentes não são removidos

---

## Análise Manual dos Projetos

### Projeto 1 — code-smells-project (Python/Flask)

**Stack:** Python 3, Flask, raw `sqlite3`, sem ORM  
**Arquitetura original:** Monolítica — `app.py` único com ~800 linhas  
**Problemas principais:**
- SQL Injection via f-strings em 4 rotas
- Endpoint `/admin/query` sem autenticação (SQL shell aberto)
- Senhas em MD5 sem salt
- Chave secreta hardcoded
- Hash de senha retornado nas respostas da API
- N+1 queries no endpoint de pedidos

**Resultado:** Refatorado em 12 arquivos MVC (`src/models/`, `src/controllers/`, `src/views/`, `src/middlewares/`)

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

**Stack:** Node.js, Express, `sqlite3` (callbacks async), better-sqlite3 (após refatoração)  
**Arquitetura original:** God Class `AppManager` — 1200+ linhas em arquivo único  
**Problemas principais:**
- Banco de dados em memória (`:memory:`) — dados perdidos a cada restart
- Senhas em base64 (reversível, não é criptografia)
- JWT secret hardcoded
- `/admin/financial-report` sem autenticação
- Callback hell com N+1 no relatório financeiro
- Registros órfãos ao deletar usuário

**Resultado:** Refatorado com `createApp()` factory, `better-sqlite3` síncrono, bcrypt, arquivos em `src/models/`, `src/controllers/`, `src/routes/`, `src/middlewares/`

### Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)

**Stack:** Python 3, Flask, Flask-SQLAlchemy ORM, SQLite  
**Arquitetura original:** Parcialmente organizada — models separados, mas rotas "gordas" com lógica de negócio  
**Problemas principais:**
- `SECRET_KEY = 'super-secret-key-123'` hardcoded
- Senha SMTP `'senha123'` hardcoded no `NotificationService`
- N+1 ORM queries no listing de tasks (lazy loading em loop)
- N+1 no relatório summary (query por usuário em loop)
- Lógica de negócio embutida nos route handlers
- Sem tratamento centralizado de erros

**Resultado:** Refatorado com `create_app()` factory em `src/`, controllers separados, `joinedload` para eliminar N+1, `register_error_handlers()` centralizado

---

## Construção da Skill

### Decisões de design

**Por que 3 fases com pausas?**  
Refatoração automática é destrutiva. As pausas entre fases garantem que o desenvolvedor revisou o diagnóstico antes de qualquer arquivo ser modificado. A Fase 2 é a mais importante: o desenvolvedor pode ver exatamente quais problemas serão corrigidos antes de autorizar.

**Por que o catálogo de anti-padrões é separado do playbook?**  
O catálogo (`02`) descreve *o que detectar* (sintomas, nomes padronizados). O playbook (`05`) descreve *como transformar* (before/after code). Separar permite referenciar padrões pelo ID (AP-02, PT-03) sem duplicar código.

**Por que `04-mvc-architecture-guidelines.md` cobre Python e Node.js?**  
Os 3 projetos usam tecnologias diferentes. As guidelines são agnósticas à linguagem na estrutura lógica (Controller não acessa `request`, Model não conhece HTTP) e fornecem exemplos concretos em ambas as linguagens para a IA adaptar corretamente.

### Padrões de transformação implementados

| ID | Transformação |
|----|---------------|
| PT-01 | Monolito → Config centralizada com env vars |
| PT-02 | SQL concat/f-string → queries parametrizadas |
| PT-03 | MD5/base64 → bcrypt com salt aleatório |
| PT-04 | God class → Controllers com injeção de dependência |
| PT-05 | Fat routes → Thin HTTP blueprints / routers |
| PT-06 | N+1 loop queries → JOIN / joinedload / GROUP BY |
| PT-07 | Except silencioso → Centralized error handler |
| PT-08 | Dados sensíveis em resposta → to_dict() explícito |

---

## Resultados da Refatoração

### Projeto 1 (code-smells-project)

```
GET /produtos       → 200 OK
GET /health         → 200 OK  {"status":"ok","database":"connected"}
GET /produtos/busca → 200 OK
POST /login         → 200 OK  (senha não no response)
```

### Projeto 2 (ecommerce-api-legacy)

```
GET /api/courses    → 200 OK
GET /api/courses/1  → 200 OK
GET /health         → 200 OK  {"status":"ok","database":"connected"}
```

### Projeto 3 (task-manager-api)

```
GET /health         → 200 OK  {"status":"ok","database":"connected"}
GET /tasks          → 200 OK
GET /categories     → 200 OK
POST /users         → 201 Created (sem campo password)
POST /login         → 200 OK  (user keys: id,name,email,role,active,created_at)
POST /tasks         → 201 Created
```

---

## Como Executar

### Projeto 1 — code-smells-project

```bash
cd desafios/desafio-3-skill-refactor-arch/code-smells-project
pip install -r requirements.txt
python src/app.py
# ou via entry point original:
python app.py
```

### Projeto 2 — ecommerce-api-legacy

```bash
cd desafios/desafio-3-skill-refactor-arch/ecommerce-api-legacy
npm install
node src/app.js
# ou
npm start
```

### Projeto 3 — task-manager-api

```bash
cd desafios/desafio-3-skill-refactor-arch/task-manager-api
pip install -r requirements.txt
python app.py
```

### Variáveis de ambiente (todos os projetos)

| Variável | Descrição | Default |
|----------|-----------|---------|
| `SECRET_KEY` / `JWT_SECRET` | Chave de assinatura de tokens | `dev-only-change-in-production` |
| `DATABASE_URL` / `DB_PATH` | Caminho do banco de dados | SQLite local |
| `PORT` | Porta HTTP | `5000` (Python) / `3000` (Node) |
| `SMTP_HOST` | Servidor de email | `smtp.gmail.com` |
| `SMTP_USER` | Usuário SMTP | vazio |
| `SMTP_PASSWORD` | Senha SMTP | vazio |

---

## Relatórios de Auditoria

Os relatórios completos estão em `reports/`:

- [`audit-project-1.md`](reports/audit-project-1.md) — 5 CRITICAL, 3 HIGH
- [`audit-project-2.md`](reports/audit-project-2.md) — 5 CRITICAL, 2 HIGH  
- [`audit-project-3.md`](reports/audit-project-3.md) — 3 CRITICAL, 3 HIGH
