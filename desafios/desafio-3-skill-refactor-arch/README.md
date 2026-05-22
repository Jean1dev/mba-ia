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

> Cada problema abaixo foi identificado **lendo o código real do repositório base**
> ([`devfullcycle/mba-ia-refactor-projects-skill`](https://github.com/devfullcycle/mba-ia-refactor-projects-skill)),
> está classificado segundo a escala do enunciado (CRITICAL → HIGH → MEDIUM → LOW),
> tem o **arquivo:linha** exatos e uma **justificativa** da severidade.

### Projeto 1 — code-smells-project (Python/Flask)

**Stack:** Python 3, Flask, raw `sqlite3` (sem ORM), 4 arquivos (`app.py` 88L, `controllers.py` 292L, `models.py` 314L, `database.py` 86L)  
**Arquitetura original:** Monolítica — separação só por nome de arquivo; toda a lógica/SQL está em `models.py`

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | SQL Injection generalizado por concatenação de strings em **todas** as queries dinâmicas | `models.py:28, 47-50, 92, 105-111, 127-129, 140, 148-150, 174, 188, 192, 220, 224, 280, 285-297` | Login (`models.py:105-111`) e busca (`models.py:285-297`) concatenam input do usuário direto no SQL — permite bypass de auth e extração arbitrária do banco. Falha catastrófica de segurança. |
| 2 | **CRITICAL** | Senhas armazenadas e comparadas em **plaintext** | `models.py:105-111, 127-129` + seed em `database.py:75-83` | Não há hash, MD5, nada: a coluna `senha` guarda a string literal e o login compara `senha = 'XXX'`. Pior cenário possível. |
| 3 | **CRITICAL** | Endpoint `/admin/query` sem auth aceita SQL arbitrário do body | `app.py:59-78` | "SQL shell" aberto via POST — `DROP TABLE`, `UPDATE`, `SELECT * FROM usuarios` por qualquer cliente. Equivalente a comprometer o banco. |
| 4 | **CRITICAL** | Endpoint `/admin/reset-db` sem auth apaga **tudo** | `app.py:47-57` | `DELETE FROM` em produtos, usuários, pedidos sem checagem alguma. Vandalismo em um curl. |
| 5 | **CRITICAL** | `SECRET_KEY` hardcoded **e exposta** pelo `/health` | `app.py:7` + `controllers.py:288-289` | A chave de assinatura de sessão está no source `'minha-chave-super-secreta-123'` **e** ainda é retornada em texto puro pelo endpoint público de health-check. |
| 6 | **HIGH** | Hash/plaintext de senha vazado em todas as listagens de usuário | `models.py:84, 99` | `get_todos_usuarios()` e `get_usuario_por_id()` incluem o campo `senha` no dict retornado. `GET /usuarios` devolve a senha de todo mundo. |
| 7 | **HIGH** | N+1 + cursores aninhados em `get_pedidos_usuario` e `get_todos_pedidos` | `models.py:171-201, 203-233` | Loop sobre pedidos → loop sobre itens → `SELECT nome FROM produtos WHERE id = X` por item. 3 cursores aninhados, complexidade O(n·m). |
| 8 | **HIGH** | Estado global mutável para conexão de banco | `database.py:4-10` (`db_connection = None` + `global db_connection`) | Conexão única compartilhada com `check_same_thread=False`. Inviabiliza testes paralelos e cria risco de corrupção sob carga. |
| 9 | **MEDIUM** | `DEBUG = True` em `app.config` (não só no `run`) | `app.py:8` | Habilita o reloader e o debugger interativo do Flask em qualquer ambiente. Exposição de stack-traces e PIN do debugger. |
| 10 | **MEDIUM** | Catch-all `except Exception as e: jsonify({"erro": str(e)})` em ~16 handlers | `controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 226-227, 234-235, 254-255, 261-262, 291-292` | Vaza mensagens internas (incluindo SQL) para o cliente e impede tratamento centralizado/logging adequado. |
| 11 | **MEDIUM** | Listagens sem paginação | `controllers.py:5` (`listar_produtos`), `controllers.py:128` (`listar_usuarios`), `controllers.py:229` (`listar_todos_pedidos`) | Carrega tabela inteira a cada request. Gargalo de performance previsível em produção. |
| 12 | **MEDIUM** | Validação manual duplicada entre `criar_produto` e `atualizar_produto` | `controllers.py:24-58` vs `controllers.py:64-93` | Mesma lógica copy-paste sem schema/helper. Duplicação clara, alta chance de divergir em manutenção. |
| 13 | **LOW** | `app.run(debug=True)` hardcoded no entry-point | `app.py:88` | Não lê de env. Melhoria trivial: `debug=os.getenv("DEBUG") == "true"`. |
| 14 | **LOW** | Magic numbers em regra de desconto | `models.py:256-262` (limiares `10000/5000/1000` e taxas `0.1/0.05/0.02`) | Exatamente o exemplo de "magic numbers" do enunciado. Sem constantes nomeadas. |
| 15 | **LOW** | Nomes ruins (`cursor2`, `cursor3`) e import não usado (`import sqlite3`) | `models.py:2, 187, 191, 219, 223` | Cursores numerados em sequência ao invés de nome descritivo; import morto no topo do arquivo. |

**Resultado:** Refatorado em 12 arquivos MVC (`src/models/`, `src/controllers/`, `src/views/`, `src/middlewares/`).

---

### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

**Stack:** Node.js, Express, `sqlite3` (callbacks async), 3 arquivos (`app.js` 14L, `AppManager.js` 141L, `utils.js` 25L)  
**Arquitetura original:** God class `AppManager` com DB, rotas, pagamento, log e cache em um único objeto

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | Banco SQLite em `:memory:` | `src/AppManager.js:7` | Tudo (matrículas, pagamentos, audit logs) some a cada restart. Não é "uma melhoria possível", é impedimento de funcionamento real. |
| 2 | **CRITICAL** | Credenciais hardcoded (DB password, payment gateway, SMTP) | `src/utils.js:2-6` (`dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_..."`) | "pk_live_" sugere chave de produção exposta no Git. Vazamento direto de credenciais financeiras. |
| 3 | **CRITICAL** | Seed cria usuário com senha em **plaintext** `'123'` | `src/AppManager.js:18` | `INSERT INTO users ... pass) VALUES ('Leonan', '...', '123')`. Não há `set_password`, é a string literal. |
| 4 | **CRITICAL** | "Criptografia" de senha = base64 num loop inútil | `src/utils.js:17-23` (`badCrypto`) | `Buffer.from(pwd).toString('base64')` é reversível em 1 linha. O loop de 10000 iterações concatena os 2 primeiros chars do mesmo base64 — não acrescenta segurança nenhuma. |
| 5 | **CRITICAL** | `/api/admin/financial-report` e `DELETE /api/users/:id` sem autenticação | `src/AppManager.js:80, 131` | Receita por curso e remoção de usuário disponíveis a qualquer cliente. Vazamento financeiro + capacidade destrutiva. |
| 6 | **HIGH** | God class `AppManager` controla DB, rotas, pagamento e logging | `src/AppManager.js` (arquivo todo) | Em 141 linhas: cria DB no construtor (`:7`), faz `INSERT` de seed (`:18`), define todas as rotas (`:25-138`) e processa pagamento (`:43-64`). Forte violação de SRP/MVC. |
| 7 | **HIGH** | Callback hell + N+1 em `/api/admin/financial-report` | `src/AppManager.js:80-129` | 4 níveis de callback (`db.all` cursos → `db.all` enrollments → `db.get` user → `db.get` payment), com counter manual `coursesPending`/`enrPending`. Impossível de manter. |
| 8 | **HIGH** | Registros órfãos ao deletar usuário | `src/AppManager.js:131-137` | `DELETE FROM users` mas `enrollments` e `payments` ficam apontando para `user_id` inexistente. O próprio source comenta: "matrículas e pagamentos ficaram sujos no banco". |
| 9 | **HIGH** | Número de cartão logado no `console.log` | `src/AppManager.js:45` (`console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`)`) | Card PAN + chave de gateway no log padrão. Violação de PCI e vazamento via qualquer agregador de logs. |
| 10 | **MEDIUM** | Senha default `'123456'` quando o cliente não envia uma | `src/AppManager.js:68` (`badCrypto(p \|\| "123456")`) | Em vez de erro 400, cria usuário com senha conhecida. Backdoor não-intencional. |
| 11 | **MEDIUM** | "Aprovação" de pagamento por prefixo do cartão | `src/AppManager.js:46` (`status = cc.startsWith("4") ? "PAID" : "DENIED"`) | Regra de negócio fake e fragmentada inline no handler. Em um stub seria ok, mas o handler também faz INSERT em `payments` como se fosse real. |
| 12 | **MEDIUM** | Respostas com formatos inconsistentes (string vs JSON) e status sempre 500 em erro de DB | `src/AppManager.js:38, 41, 51, 55, 60, 135` | `res.send("Curso não encontrado")` (text/plain) vs `res.status(200).json({ msg, ... })` em rotas próximas. Cliente não consegue parsear de forma uniforme. |
| 13 | **MEDIUM** | Variáveis de request com 1-3 letras (`u, e, p, cid, cc`) | `src/AppManager.js:29-33` | Em vez de `name, email, password, courseId, card`. Reduz drasticamente a legibilidade e a manutenibilidade. |
| 14 | **LOW** | Hardcoded `port: 3000` no objeto config (sem `process.env.PORT`) | `src/utils.js:6` | Trivial de externalizar; o resto da config está no mesmo lugar. |
| 15 | **LOW** | Coluna do banco chamada `pass` em vez de `password` | `src/AppManager.js:12` | Convenção ruim, conflita com palavra reservada em vários ORMs/linguagens. |
| 16 | **LOW** | Magic strings `'PAID'`, `'DENIED'`, `'4'` e mensagens misturadas PT/EN (`"Bad Request"` vs `"Pagamento recusado"`) | `src/AppManager.js:35, 38, 46-48` | Sem `enum`/constantes, sem internacionalização — caso típico do enunciado de "magic numbers/strings + nomenclatura". |
| 17 | **LOW** | Import não usado `totalRevenue` | `src/AppManager.js:2` | Trazido do `utils.js` e nunca referenciado no arquivo. |

**Resultado:** Refatorado com `createApp()` factory, `better-sqlite3` síncrono, bcrypt, arquivos em `src/models/`, `src/controllers/`, `src/routes/`, `src/middlewares/`.

---

### Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)

**Stack:** Python 3, Flask, Flask-SQLAlchemy ORM, SQLite. Estrutura inicial: `models/`, `routes/`, `services/`, `utils/`  
**Arquitetura original:** Parcialmente organizada — models separados, mas rotas "gordas" com toda a lógica de negócio

| # | Severidade | Problema | Local | Justificativa |
|---|------------|----------|-------|---------------|
| 1 | **CRITICAL** | `SECRET_KEY = 'super-secret-key-123'` hardcoded | `app.py:13` | Chave de sessão Flask em texto puro no source, sem fallback de env. |
| 2 | **CRITICAL** | Senha SMTP `'senha123'` hardcoded | `services/notification_service.py:10` | Credencial de envio de e-mail commitada no Git, ao lado de `email_user = 'taskmanager@gmail.com'`. |
| 3 | **CRITICAL** | Senhas em **MD5 sem salt** | `models/user.py:29, 32` (`hashlib.md5(pwd.encode()).hexdigest()`) | Algoritmo quebrado, sem salt, reversível por rainbow table. Vazamento total se o DB cair em mãos erradas. |
| 4 | **CRITICAL** | `to_dict()` do `User` inclui o campo `password` | `models/user.py:21` | Toda rota que devolve `user.to_dict()` (`/users`, `/login`, `/users/<id>`) vaza o hash MD5 para o cliente. |
| 5 | **HIGH** | N+1 ORM em `GET /tasks` | `routes/task_routes.py:42, 51` (`User.query.get(t.user_id)` e `Category.query.get(t.category_id)` no loop) | 2n+1 SQL para n tasks. Trivialmente resolvível com `joinedload`. |
| 6 | **HIGH** | N+1 em `GET /reports/summary` | `routes/report_routes.py:53-67` (`Task.query.filter_by(user_id=u.id)` no loop sobre usuários) | Em relatório a degradação é ainda pior — endpoint usado para dashboards. |
| 7 | **HIGH** | N+1 em `GET /categories` e `/tasks/stats` | `routes/report_routes.py:161-163`, `routes/task_routes.py:281-287` | `Task.query.filter_by(category_id=c.id).count()` por categoria; `Task.query.all()` só para varrer e contar overdue em Python. |
| 8 | **HIGH** | Lógica de negócio inteiramente dentro de route handlers | `routes/task_routes.py:30-39, 70-80, 281-296`, `routes/user_routes.py:42-90`, `routes/report_routes.py:13-101` | Cálculo de overdue, completion rate, validação e serialização HTTP misturados na mesma função. Controllers/services não existem. |
| 9 | **MEDIUM** | `except:` bare engolindo todas as exceções (incluindo `KeyboardInterrupt`) | `routes/task_routes.py:62-63, 137-138, 204-205, 236-238`, `routes/user_routes.py:130-132, 149-151`, `routes/report_routes.py:186-188, 207-209, 221-223` | Mascara erros reais (`ConnectionError` retorna 500 genérico), impede observabilidade e bloqueia sinais de OS. |
| 10 | **MEDIUM** | Cálculo de "overdue" duplicado em 6 lugares com regra idêntica | `routes/task_routes.py:30-39, 70-80, 283-287`, `routes/report_routes.py:33-43, 132-135`, `routes/user_routes.py:171-180` | Mesmo `if t.due_date and t.due_date < datetime.utcnow() and t.status not in ('done','cancelled')` reescrito 6×. Bug em um deles passa despercebido. |
| 11 | **MEDIUM** | Sem paginação em `/tasks`, `/users`, `/categories` | `routes/task_routes.py:14`, `routes/user_routes.py:12`, `routes/report_routes.py:159` | Listagens carregam tabela inteira na memória. Padrão MEDIUM clássico de performance. |
| 12 | **MEDIUM** | Validações duplicadas e fora dos schemas declarados em `utils/helpers.py` | `routes/task_routes.py:110, 113`, `routes/user_routes.py:61, 64, 71` vs constantes em `utils/helpers.py:110-117` (não usadas) | `VALID_STATUSES`, `MIN/MAX_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH` existem como constantes mas as rotas reescrevem os literais inline. |
| 13 | **LOW** | `/health` expõe `timestamp` do servidor | `app.py:24` | `{'status': 'ok', 'timestamp': str(datetime.datetime.now())}`. Dado desnecessário no health. |
| 14 | **LOW** | `app.run(debug=True)` hardcoded | `app.py:34` | Sem leitura de `os.environ`. Melhoria trivial. |
| 15 | **LOW** | Imports não utilizados em vários arquivos | `routes/task_routes.py:7` (`json, os, sys, time`), `routes/user_routes.py:6` (`hashlib, json`), `routes/report_routes.py:8` (`json`), `utils/helpers.py:3-7` (`os, json, sys, math, hashlib`) | Ruído no topo dos arquivos — afeta legibilidade, é o tipo de problema LOW do enunciado. |
| 16 | **LOW** | Magic numbers (`7` dias, `priority <= 2` como "high") | `routes/report_routes.py:45, 129` | Constantes nomeadas (`RECENT_DAYS = 7`, `HIGH_PRIORITY = 2`) resolveriam — é o exemplo literal do enunciado de "magic numbers soltos". |
| 17 | **LOW** | `type(tags) == list` em vez de `isinstance(tags, list)` | `routes/task_routes.py:141, 210` | Antipattern de checagem de tipo em Python. Não quebra, mas é melhoria de legibilidade/correção. |
| 18 | **LOW** | Token "JWT" hardcoded literalmente como `'fake-jwt-token-' + str(user.id)` | `routes/user_routes.py:210` | Não chega a CRITICAL porque ninguém valida esse "token" do outro lado, mas é caso clássico de melhoria LOW (string mágica + funcionalidade não implementada). |

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
