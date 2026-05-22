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

> Cada problema abaixo está classificado segundo a escala do enunciado
> (CRITICAL → HIGH → MEDIUM → LOW) com o **arquivo:linha** onde foi observado
> e uma **justificativa** explicando por que aquela severidade se aplica.

### Projeto 1 — code-smells-project (Python/Flask)

**Stack:** Python 3, Flask, raw `sqlite3`, sem ORM  
**Arquitetura original:** Monolítica — `app.py` único com ~800 linhas

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | SQL Injection via f-strings em 4 rotas | `app.py:87, 102, 145` | Entrada do usuário concatenada direto na query — permite leitura/escrita arbitrária do banco. É o cenário-livro de falha grave de segurança. |
| 2 | **CRITICAL** | Endpoint `/admin/query` sem autenticação | `app.py:312` | "SQL shell" aberto via POST. Qualquer cliente executa `DROP TABLE`. Falha completa de controle de acesso. |
| 3 | **CRITICAL** | Senhas em MD5 sem salt | `app.py:198` | Algoritmo quebrado + sem salt → rainbow table reverte hashes em segundos. Expõe credenciais de todos os usuários se o DB vazar. |
| 4 | **CRITICAL** | `SECRET_KEY` hardcoded no fonte | `app.py:12` | Chave de assinatura de sessão commitada no Git → qualquer pessoa com acesso ao repo forja sessões válidas. |
| 5 | **HIGH** | God Class — `app.py` com ~800 linhas | `app.py` (arquivo inteiro) | Mistura roteamento, regras de negócio, queries SQL, validação e bootstrap. Inviabiliza teste unitário e qualquer evolução isolada. Forte violação de MVC/SOLID. |
| 6 | **HIGH** | N+1 queries no listing de pedidos | `app.py:178` | Loop Python executando `SELECT` por pedido. Em 100 pedidos = 101 queries. Degrada com o volume. |
| 7 | **MEDIUM** | Validação ausente nas rotas POST | `app.py:198, 240` | Endpoints aceitam JSON sem checar tipo/obrigatoriedade. Um payload sem `email` causa `KeyError → 500` em vez de `400`. Padrão ruim e gargalo de manutenção. |
| 8 | **MEDIUM** | `GET /produtos` sem paginação | `app.py:55` | Retorna o catálogo inteiro em cada chamada. Em produção, com milhares de produtos, vira gargalo claro de performance — entra em MEDIUM por ser duplicado em várias rotas list. |
| 9 | **MEDIUM** | `try/except` bare engolindo exceções | `app.py:289, 360` | `except:` sem logging mascara erros reais e retorna `200` em situações de falha. Inconsistência de comportamento ao longo da API. |
| 10 | **LOW** | `app.run(debug=True)` hardcoded | `app.py:799` | Debug do Flask sempre ligado expõe o debugger PIN na rede. Não é falha arquitetural grave, mas é melhoria óbvia: bastaria ler de env. |
| 11 | **LOW** | Magic numbers espalhados (`100`, `10`, `1`) | `app.py:148, 215` | Limites e flags numéricas soltas no código (ex.: `LIMIT 100`, `if status == 1`). Reduz legibilidade — caso típico de severidade LOW. |
| 12 | **LOW** | Nomenclatura misturada PT/EN | `app.py` (geral) | `produtos`, `usuarios`, `def get_user_data`, `categoria`, `email` no mesmo arquivo. Não quebra nada, mas é o exemplo do enunciado de "nomenclatura de variáveis ruins". |

**Resultado:** Refatorado em 12 arquivos MVC (`src/models/`, `src/controllers/`, `src/views/`, `src/middlewares/`).

---

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

**Stack:** Node.js, Express, `sqlite3` (callbacks async), `better-sqlite3` (após refatoração)  
**Arquitetura original:** God Class `AppManager` — 1200+ linhas em arquivo único

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | Banco `:memory:` em produção | `src/database.js:3` | Todos os dados (cursos, pagamentos, matrículas) somem a cada restart. Impede a aplicação de funcionar corretamente — exatamente o exemplo do enunciado de falha CRITICAL. |
| 2 | **CRITICAL** | "Criptografia" de senha em base64 | `src/models/UserModel.js:45` | Base64 é codificação, não criptografia. `Buffer.from(b64, 'base64')` reverte a senha em uma linha. Equivale a guardar plaintext. |
| 3 | **CRITICAL** | JWT secret e payment key hardcoded | `src/app.js:8` | `super-secret-jwt-key-2024` e `pk_test_hardcoded` no source. Vazamento total de credenciais ao commitar. |
| 4 | **CRITICAL** | `/api/admin/financial-report` sem auth | `src/app.js:142` | Relatório de receita exposto sem qualquer verificação. Vazamento direto de dados financeiros. |
| 5 | **CRITICAL** | God Class `AppManager` (1200+ linhas) | `src/app.js` (arquivo inteiro) | DB, regras de negócio, rotas, e-mail e pagamento dentro de uma classe com estado global mutável. Violação total da separação de responsabilidades. |
| 6 | **HIGH** | Callback hell com N+1 no relatório financeiro | `src/app.js:380-450` | `db.all()` aninhado em loop sobre cursos — pyramid-of-doom + O(n) queries. Mantém escala ruim e é praticamente impossível de testar. |
| 7 | **HIGH** | Registros órfãos ao deletar usuário | `src/app.js:510` | `deleteUser` apaga só a linha do usuário. `payments` e `enrollments` ficam com `user_id` apontando para nada. Quebra integridade referencial. |
| 8 | **MEDIUM** | Sem validação de payload em rotas POST/PUT | `src/app.js:200, 245, 280` | Nenhum `joi`, `zod` ou `express-validator`. Campos obrigatórios checados ad-hoc ou nem checados. Padrão inconsistente em toda a API. |
| 9 | **MEDIUM** | Sem rate limiting nas rotas de auth | `src/app.js:170` | `/api/login` aberto para brute force ilimitado. Não é falha grave por si só (existem outros controles), mas é gargalo conhecido e padrão ruim. |
| 10 | **MEDIUM** | Status codes inconsistentes (sempre 200) | `src/app.js` (várias rotas) | Erros de validação retornam `200 { error: ... }` em vez de `400/404`. Clientes não conseguem reagir corretamente. |
| 11 | **LOW** | `console.log` espalhado como logging | `src/app.js:55, 88, 412` | Sem nível, sem timestamp, sem `winston/pino`. Funciona, mas é melhoria óbvia de legibilidade/operação. |
| 12 | **LOW** | Magic numbers em regras de negócio | `src/app.js:320` (`if (price > 1000) discount = 0.1`) | Valores de desconto e thresholds soltos no meio do código. Exemplo direto do "magic numbers" do enunciado. |
| 13 | **LOW** | Uso indevido de `var` e nomes pouco descritivos | `src/app.js` (geral) | `var x`, `var data`, `var tmp` em código moderno Node. Não quebra, mas é melhoria de legibilidade clássica. |

**Resultado:** Refatorado com `createApp()` factory, `better-sqlite3` síncrono, bcrypt, arquivos em `src/models/`, `src/controllers/`, `src/routes/`, `src/middlewares/`.

---

### Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)

**Stack:** Python 3, Flask, Flask-SQLAlchemy ORM, SQLite  
**Arquitetura original:** Parcialmente organizada — models separados, mas rotas "gordas" com lógica de negócio

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | `SECRET_KEY` hardcoded + senha SMTP `'senha123'` | `app.py:13`, `services/notification_service.py:8-9` | Credenciais sensíveis em texto puro no source. Vaza a chave de sessão e a senha de envio de e-mail no Git. |
| 2 | **HIGH** | Lógica de negócio embutida em route handlers | `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py` | Validação, cálculo de overdue/completion rate, regra de permissão e serialização HTTP tudo dentro da mesma função. Forte violação de MVC — controllers/services não existem. |
| 3 | **HIGH** | N+1 ORM queries no listing de tasks | `routes/task_routes.py:42-57` | `User.query.get()` e `Category.query.get()` chamados dentro do loop por task → 2n+1 queries. Degrada drasticamente com volume. |
| 4 | **HIGH** | N+1 no `GET /reports/summary` | `routes/report_routes.py:53-68` | `Task.query.filter_by(user_id=u.id)` dentro de loop sobre usuários. Mesma classe de problema, em rota de relatório (impacto ainda maior). |
| 5 | **MEDIUM** | Sem tratamento centralizado de erros | `app.py`, `routes/*.py` | Cada handler tem seu próprio `try/except` retornando formato diferente. Sem `@app.errorhandler` registrado. Inconsistência de contrato da API. |
| 6 | **MEDIUM** | Endpoints `GET /tasks` e `GET /users` sem paginação | `routes/task_routes.py:30`, `routes/user_routes.py:25` | Listings carregam a tabela inteira na memória. Em escala vira gargalo de performance — exatamente o tipo de problema MEDIUM do enunciado. |
| 7 | **MEDIUM** | Validações de input ausentes nas rotas POST | `routes/task_routes.py:75`, `routes/user_routes.py:40` | Nenhum schema (marshmallow/pydantic). Campos obrigatórios checados com `if not data.get(...)` ad-hoc, retornando mensagens diferentes em cada rota. |
| 8 | **LOW** | `/health` expõe `timestamp` do servidor | `app.py:23` | Retornar `datetime.now()` no health não é falha grave, mas é dado desnecessário que assiste reconhecimento. Melhoria simples. |
| 9 | **LOW** | `print()` usado para logging | `routes/task_routes.py:88`, `services/notification_service.py:25` | Sem `logging.getLogger`, sem nível. Funciona, mas o enunciado coloca esse tipo de melhoria de legibilidade como LOW. |
| 10 | **LOW** | Magic numbers em regra de overdue | `routes/task_routes.py:50` (`if (datetime.now() - due).days > 7`) | `7` solto no código sem constante nomeada (`OVERDUE_DAYS`). Caso clássico do "magic number" listado no enunciado. |

**Resultado:** Refatorado com `create_app()` factory em `src/`, controllers separados, `joinedload` para eliminar N+1, `register_error_handlers()` centralizado.

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
