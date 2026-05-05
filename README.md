# Desafio Skills — Refatoração Arquitetural Automatizada

Implementação do desafio de criação de Skills para refatoração automatizada de projetos legados para o padrão MVC, utilizando **Claude Code** com Custom Skills.

---

## Como Executar

### Pré-requisitos
- Claude Code instalado e configurado
- Python 3.9+ (para projetos Python)
- Node.js 18+ (para projeto Node.js)

### Executar a skill em cada projeto

```bash
# Projeto 1 — Python/Flask E-commerce
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — Node.js/Express LMS
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — Python/Flask Task Manager
cd ../task-manager-api
claude "/refactor-arch"
```

### Validar que a refatoração funcionou

```bash
# Projeto 1
cd code-smells-project
pip install -r requirements.txt
python src/app.py &
curl http://localhost:5000/api/v1/produtos

# Projeto 2
cd ecommerce-api-legacy
npm install
node src/app.js &
curl http://localhost:3000/cursos

# Projeto 3
cd task-manager-api
pip install -r requirements.txt
python src/app.py &
curl http://localhost:5001/api/v1/tasks
```

---

## Análise Manual

### Projeto 1 — code-smells-project (Python/Flask E-commerce API)

| Severidade | Problema | Arquivo | Linha |
|---|---|---|---|
| CRITICAL | SECRET_KEY hardcoded `"minha-chave-super-secreta-123"` | app.py | 13 |
| CRITICAL | SQL Injection por concatenação de string | models.py | 38 |
| CRITICAL | SQL Injection por f-string interpolation | models.py | 101 |
| CRITICAL | Senha com MD5 sem salt (algoritmo quebrado) | models.py | 116, 138 |
| HIGH | God Class — models.py com 4 domínios + lógica de negócio | models.py | 1–212 |
| HIGH | Senhas retornadas na resposta da API sem autenticação | controllers.py | 37–39 |
| HIGH | Token falso sem JWT real nem expiração | controllers.py | 64 |
| HIGH | Ausência de autenticação em rotas sensíveis | app.py | 21–30 |
| MEDIUM | N+1 query problem em `get_all()` | models.py | 18–30 |
| MEDIUM | Race condition no checkout sem transação | models.py | 163–167 |
| MEDIUM | CORS liberado sem restrição de origem | app.py | 15 |
| LOW | `debug=True` habilitado em produção | app.py | 37 |
| LOW | Print de debug com credenciais em texto plano | models.py | 134 |
| LOW | Variáveis nomeadas `x`, `y`, `z` | models.py | 107–109 |

**Por que esses problemas são relevantes:**
- Os SQLi em modelos.py são exploits triviais que expõem toda a base de dados
- O MD5 sem salt torna rainbow table attacks triviais após um vazamento de banco
- O God Class com 212 linhas é completamente untestable em isolamento

---

### Projeto 2 — ecommerce-api-legacy (Node.js/Express LMS API)

| Severidade | Problema | Arquivo | Linha |
|---|---|---|---|
| CRITICAL | JWT_SECRET hardcoded no código-fonte | src/AppManager.js | 8 |
| CRITICAL | God Class gerenciando 6 responsabilidades diferentes | src/AppManager.js | 1–135 |
| CRITICAL | JWT sem algoritmo explícito (deprecated default) | src/AppManager.js | 55 |
| HIGH | Toda lógica de checkout no AppManager | src/AppManager.js | 72–112 |
| HIGH | Auth inline duplicado em 3 rotas | src/app.js | 40–62 |
| HIGH | Cache sem TTL e com bug de invalidação | src/AppManager.js | 114–117 |
| HIGH | POST /cursos sem autenticação | src/app.js | 47–50 |
| HIGH | Erro de banco exposto diretamente ao cliente | src/AppManager.js | 130 |
| MEDIUM | N+1 query em getMatriculasAluno | src/AppManager.js | 119–124 |
| MEDIUM | Race condition no controle de vagas | src/AppManager.js | 79–81 |
| MEDIUM | Sem verificação de matrícula duplicada | src/AppManager.js | 88–91 |
| MEDIUM | Sem validação de entrada nas rotas | src/app.js | 30–50 |
| LOW | Estado global mutável (activeUsers, sessionStore) | src/utils.js | 7–8 |
| LOW | Porta hardcoded sem env var | src/app.js | 72 |
| LOW | Função slugify não utilizada | src/utils.js | 23–25 |
| LOW | Magic strings de cupom inline | src/AppManager.js | 83–87 |

**Por que esses problemas são relevantes:**
- O AppManager é um anti-pattern extremo: 135 linhas, 6 responsabilidades, impossível de testar
- A ausência de verificação de matrícula duplicada causa cobranças múltiplas no mesmo curso
- O bug de cache pode mostrar vagas erradas indefinidamente após matrículas

---

### Projeto 3 — task-manager-api (Python/Flask Task Manager)

| Severidade | Problema | Arquivo | Linha |
|---|---|---|---|
| CRITICAL | SECRET_KEY hardcoded | app.py | 11 |
| CRITICAL | SQL Injection via f-string em TaskModel | models/task.py | 19 |
| CRITICAL | Senhas armazenadas em texto plano | models/user.py | 25–31 |
| HIGH | Token de auth fake e previsível | routes/auth.py | 17 |
| HIGH | Nenhuma autenticação nas rotas de tasks | routes/tasks.py | 9–50 |
| HIGH | Service mistura acesso a banco com orquestração | services/task_service.py | 11–21 |
| HIGH | Comparação de senha em texto plano (sem bcrypt) | models/user.py | 13–17 |
| MEDIUM | N+1 query em get_tasks_with_stats | services/task_service.py | 13–22 |
| MEDIUM | Sem validação de status e prioridade | routes/tasks.py | 25–29 |
| MEDIUM | Sem verificação de permissão para deletar | routes/tasks.py | 39–43 |
| MEDIUM | CORS sem restrição de origem | app.py | 7 |
| LOW | debug=True em produção | app.py | 19 |
| LOW | Função `calculate_progress` nunca utilizada | utils/helpers.py | 10–12 |
| LOW | Magic strings de status duplicadas | services/task_service.py | 21–23 |

**Por que esses problemas são relevantes:**
- Mesmo sendo parcialmente organizado (tem models/, routes/, services/), ainda contém SQLi e senhas em texto plano
- A autenticação não existe de fato — qualquer pessoa pode acessar e deletar qualquer task
- O projeto demonstra que organização em pastas não equivale a arquitetura segura

---

## Construção da Skill

### Estrutura do SKILL.md e Arquivos de Referência

A skill foi organizada em 5 arquivos de referência temáticos + o SKILL.md de orquestração:

```
.claude/skills/refactor-arch/
├── SKILL.md                        # Orquestrador das 3 fases
├── 01-project-analysis.md          # Heurísticas de detecção de stack
├── 02-antipatterns-catalog.md      # Catálogo com AP-01 a AP-20
├── 03-audit-report-template.md     # Template padronizado do relatório
├── 04-mvc-architecture-guidelines.md  # Regras e exemplos de MVC alvo
└── 05-refactoring-playbook.md      # Padrões de transformação PT-01 a PT-08
```

**Decisões de design:**
- Separação em 5 arquivos temáticos (em vez de 1 arquivo grande) permite que o agente carregue apenas o conhecimento necessário por fase
- O `SKILL.md` é um prompt de orquestração que instrui o agente a ler os arquivos de referência antes de cada fase
- A confirmação explícita (`[y/n]`) é obrigatória na transição entre Fase 2 e Fase 3 — o humano sempre revisa antes de qualquer modificação

### Catálogo de Anti-Patterns

O catálogo cobre 20 anti-patterns (AP-01 a AP-20) distribuídos por severidade:

| Severidade | Anti-patterns |
|---|---|
| CRITICAL | Hardcoded Credentials, SQL Injection, God Class, Plaintext Password, Exposed Sensitive Data |
| HIGH | Business Logic in Controller, No Auth, Inline Auth Duplication, Global Mutable State, No DI |
| MEDIUM | N+1 Query, Race Condition, Missing Validation, No API Versioning, Unbounded Queries, Deprecated APIs, No Error Handler |
| LOW | Magic Numbers, Debug in Production, Poor Naming / Dead Code |

**Inclusão de APIs deprecated:** A tabela `Deprecated APIs Quick Reference` em `02-antipatterns-catalog.md` cobre Flask, Node.js, Express, JWT e bcrypt.

### Como a Skill é Agnóstica de Tecnologia

- A Fase 1 detecta automaticamente Python vs Node.js pela presença de `requirements.txt` vs `package.json`
- O catálogo cobre sinais de detecção para Python E JavaScript (ex: f-string E template literal para SQL Injection)
- O playbook tem exemplos `before/after` nas duas linguagens para cada padrão
- O `SKILL.md` inclui tabela de equivalências por tecnologia (Config, Auth, Error Handler, DI)

### Desafios e Soluções

1. **Projeto 3 já parcialmente organizado:** A skill precisava detectar que mesmo com `models/`, `routes/` e `services/`, ainda havia SQLi e senhas em texto plano. A solução foi o catálogo de anti-patterns cobrir tanto problemas estruturais quanto de segurança e código.

2. **N+1 queries difíceis de detectar sem executar o código:** Os sinais de detecção foram definidos como padrões textuais (SQL query dentro de loop `for`/`.map()`), o que funciona estaticamente.

3. **Garantir que a skill pausa antes de modificar arquivos:** O `SKILL.md` tem instrução explícita `"Wait for user confirmation. Do NOT modify any files before receiving 'y'."`.

---

## Resultados

### Resumo dos Relatórios de Auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| code-smells-project | 4 | 5 | 3 | 3 | 15 |
| ecommerce-api-legacy | 3 | 6 | 4 | 4 | 17 |
| task-manager-api | 3 | 4 | 4 | 3 | 14 |

### Comparação Antes/Depois — code-smells-project

**Antes:**
```
code-smells-project/
├── app.py           # routes + config hardcoded
├── models.py        # God class: 4 domínios + business logic
├── controllers.py   # logic + HTTP mixed
└── database.py
```

**Depois (MVC):**
```
code-smells-project/
├── src/
│   ├── config/settings.py           # Config via env vars
│   ├── database.py
│   ├── models/
│   │   ├── produto_model.py         # Data access only
│   │   ├── usuario_model.py
│   │   └── pedido_model.py
│   ├── controllers/
│   │   ├── produto_controller.py    # Business logic
│   │   ├── usuario_controller.py
│   │   └── pedido_controller.py
│   ├── views/routes.py              # HTTP layer only
│   ├── middlewares/error_handler.py # Centralized errors
│   └── app.py                       # Composition root
└── requirements.txt                 # + bcrypt added
```

### Comparação Antes/Depois — ecommerce-api-legacy

**Antes:**
```
ecommerce-api-legacy/src/
├── app.js         # routes + inline auth + config
├── AppManager.js  # God class: DB + auth + checkout + cache
└── utils.js       # global mutable state
```

**Depois (MVC):**
```
ecommerce-api-legacy/src/
├── config/settings.js
├── database.js
├── models/
│   ├── CursoModel.js
│   ├── AlunoModel.js
│   └── MatriculaModel.js
├── controllers/
│   ├── AuthController.js
│   ├── CursoController.js
│   └── CheckoutController.js
├── routes/
│   ├── auth.routes.js
│   ├── cursos.routes.js
│   └── checkout.routes.js
├── middlewares/
│   ├── auth.js
│   └── errorHandler.js
└── app.js          # Composition root
```

### Comparação Antes/Depois — task-manager-api

**Antes:**
```
task-manager-api/
├── app.py              # SECRET_KEY hardcoded
├── models/task.py      # SQL Injection
├── models/user.py      # Passwords in plaintext
├── routes/tasks.py     # No auth
├── routes/auth.py      # Fake token
└── services/task_service.py  # N+1 queries
```

**Depois (MVC aprimorado):**
```
task-manager-api/
├── src/
│   ├── config/settings.py      # Config + constants
│   ├── database.py
│   ├── models/
│   │   ├── task_model.py       # JOIN eliminates N+1
│   │   └── user_model.py       # bcrypt verification
│   ├── controllers/
│   │   ├── auth_controller.py  # Secure auth
│   │   └── task_controller.py  # Validation
│   ├── routes/
│   │   ├── auth_routes.py
│   │   └── task_routes.py
│   ├── middlewares/error_handler.py
│   └── app.py
```

### Checklist de Validação

#### Projeto 1 — code-smells-project
- [x] Linguagem detectada corretamente: Python
- [x] Framework detectado corretamente: Flask 3.1.1
- [x] Domínio da aplicação descrito: E-commerce API (produtos, pedidos, usuários)
- [x] Número de arquivos analisados: 4 files
- [x] Relatório segue o template definido
- [x] Findings com arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo 5 findings: 15 findings
- [x] Detecção de APIs deprecated (MD5 como hash de senha)
- [x] Skill pausa antes da Fase 3
- [x] Estrutura MVC criada em src/
- [x] Config extraída para src/config/settings.py
- [x] Models com uma responsabilidade cada
- [x] Views/Routes separadas (src/views/routes.py)
- [x] Controllers concentram lógica de negócio
- [x] Error handling centralizado (src/middlewares/error_handler.py)
- [x] Entry point claro (src/app.py — composition root)
- [x] Aplicação inicia sem erros ✓
- [x] Endpoints originais respondem ✓

#### Projeto 2 — ecommerce-api-legacy
- [x] Linguagem detectada: Node.js
- [x] Framework detectado: Express 4.18.2
- [x] Domínio: LMS API (cursos, alunos, matrículas, checkout)
- [x] Arquivos analisados: 3 files
- [x] 17 findings identificados
- [x] 3 CRITICAL + 6 HIGH incluídos
- [x] Detecção de JWT sem algoritmo explícito (deprecated)
- [x] Skill pausou antes de modificar arquivos
- [x] Estrutura MVC criada
- [x] Aplicação inicia sem erros ✓
- [x] Endpoints /cursos, /auth/login, /checkout respondem ✓

#### Projeto 3 — task-manager-api
- [x] Linguagem detectada: Python
- [x] Framework detectado: Flask 3.1.1
- [x] Domínio: Task Manager API
- [x] Arquivos analisados: 10 files
- [x] 14 findings identificados
- [x] 3 CRITICAL incluídos
- [x] Skill identificou problemas mesmo em projeto parcialmente organizado
- [x] Fase 3 melhorou estrutura sem quebrar endpoints
- [x] Aplicação inicia sem erros ✓
- [x] Todos endpoints respondem ✓

### Comportamento da Skill em Stacks Diferentes

- **Python/Flask (Projetos 1 e 3):** A skill detectou corretamente ambos. No Projeto 3 (parcialmente organizado), identificou que estrutura de pastas ≠ ausência de problemas — encontrou SQLi e senhas em plaintext que não seriam óbvios sem análise profunda.

- **Node.js/Express (Projeto 2):** A skill se adaptou automaticamente, usando sinais de detecção diferentes (template literals ao invés de f-strings para SQLi, `process.env` ao invés de `os.environ` para config) e gerou código de refatoração correto para o ecossistema Node.js.

---

## Estrutura do Repositório

```
mba-ia/
├── README.md
│
├── code-smells-project/
│   ├── .claude/skills/refactor-arch/   # Skill original
│   ├── src/                            # Código refatorado (MVC)
│   ├── reports/audit-project-1.md
│   ├── app.py, models.py, controllers.py, database.py  # Legado (referência)
│   └── requirements.txt
│
├── ecommerce-api-legacy/
│   ├── .claude/skills/refactor-arch/   # Cópia da skill
│   ├── src/                            # Código refatorado (MVC)
│   ├── reports/audit-project-2.md
│   └── package.json
│
├── task-manager-api/
│   ├── .claude/skills/refactor-arch/   # Cópia da skill
│   ├── src/                            # Código refatorado (MVC)
│   ├── reports/audit-project-3.md
│   └── requirements.txt
│
└── reports/
    ├── audit-project-1.md
    ├── audit-project-2.md
    └── audit-project-3.md
```
