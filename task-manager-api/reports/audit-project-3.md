================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.1.1
Files:   10 analyzed | ~293 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] Hardcoded SECRET_KEY
File: app.py:11
Description: `app.config["SECRET_KEY"] = "task-manager-secret-key-123"` hardcoded diretamente no entry point da aplicação. Qualquer pessoa com acesso ao repositório conhece a chave.
Impact: Comprometimento de sessões, tokens e qualquer dado protegido pela chave secreta.
Recommendation: Usar `os.environ.get("SECRET_KEY")` via `Config` em `src/config/settings.py`.

### [CRITICAL] SQL Injection via f-string em TaskModel
File: models/task.py:19
Description: `f"SELECT * FROM tasks WHERE id = {task_id}"` interpola o parâmetro `task_id` diretamente na string SQL. O valor é recebido diretamente da URL via Flask (`<task_id>` string) e passado sem sanitização.
Impact: Permite extração de qualquer dado do banco de dados através de SQL Injection clássico.
Recommendation: Usar query parametrizada: `conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))`.

### [CRITICAL] Senhas Armazenadas em Texto Plano
File: models/user.py:25-31, database.py:40-41
Description: `UserModel.create()` insere a senha diretamente sem hashing: `conn.execute("INSERT INTO users ... VALUES (?, ?, ?)", (username, password, email))`. Dados de seed também usam senha literal.
Impact: Em caso de vazamento do banco de dados, todas as senhas dos usuários ficam expostas em texto plano. Violação grave da LGPD/GDPR.
Recommendation: Hash com bcrypt antes de armazenar: `bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()`.

### [HIGH] Token de Autenticação Fake e Previsível
File: routes/auth.py:17
Description: `token = f"token-{user['id']}-{user['username']}"` gera tokens sem criptografia, sem assinatura e completamente previsíveis. Qualquer pessoa que conheça o ID e username pode forjar o token.
Impact: Autenticação inexistente na prática — qualquer usuário pode se passar por outro.
Recommendation: Usar `secrets.token_hex(32)` com armazenamento server-side, ou JWT com chave secreta via `PyJWT`.

### [HIGH] Nenhuma Autenticação nas Rotas de Tasks
File: routes/tasks.py:9-50
Description: Todas as rotas — incluindo `DELETE /tasks/<id>` e `PATCH /tasks/<task_id>/status` — não verificam autenticação. Qualquer requisição anônima pode deletar tasks ou alterar status.
Impact: Qualquer usuário pode deletar tasks de qualquer projeto sem estar autenticado.
Recommendation: Implementar decorator `@require_auth` e aplicar em todas as rotas de escrita.

### [HIGH] Lógica de Negócio Misturada no Service com Acesso Direto ao Banco
File: services/task_service.py:11-21
Description: `TaskService.get_tasks_with_stats()` abre nova conexão com o banco (`get_db()`) enquanto já recebe tasks via model, misturando acesso a dados com orquestração de negócio no mesmo método.
Impact: Service acoplado à implementação de banco, impossível testar sem banco real. Viola o princípio de separação de responsabilidades.
Recommendation: Mover a query de `assignee` para o `TaskModel` usando LEFT JOIN. Controller/Service apenas orquestra.

### [HIGH] Ausência de Autenticação Verificada — Comparação Direta de Senha em Texto Plano
File: models/user.py:13-17
Description: `authenticate()` compara senha diretamente: `WHERE username = ? AND password = ?`. Como as senhas estão em texto plano, qualquer conhecimento direto da senha (ou do hash) permite login.
Impact: Sem bcrypt, não há proteção contra timing attacks nem contra rainbow tables após vazamento.
Recommendation: Buscar user por username e comparar com `bcrypt.checkpw(password.encode(), stored_hash.encode())`.

### [MEDIUM] N+1 Query em get_tasks_with_stats
File: services/task_service.py:13-22
Description: Para cada task na lista, uma query separada busca o usuário assignee: `conn.execute("SELECT id, username FROM users WHERE id = ?", (task["assignee_id"],))` dentro de um loop.
Impact: Para 50 tasks, são executadas 51 queries. Performance degrada linearmente.
Recommendation: Usar `LEFT JOIN` no `TaskModel.find_all()`: `SELECT t.*, u.username as assignee_name FROM tasks t LEFT JOIN users u ON u.id = t.assignee_id`.

### [MEDIUM] Sem Validação de Status e Prioridade nas Rotas
File: routes/tasks.py:25-29, models/task.py:27-31
Description: `PATCH /tasks/<id>/status` não valida se o valor de `status` é um dos valores permitidos (`todo`, `in_progress`, `done`). `TaskModel.create()` aceita qualquer valor de `priority` sem verificar range 1-5.
Impact: Dados inválidos podem ser inseridos no banco, corrompendo o estado da aplicação.
Recommendation: Definir constantes `VALID_STATUSES = {"todo", "in_progress", "done"}` e validar antes de persistir.

### [MEDIUM] Sem Verificação de Permissão para Deletar Tasks
File: routes/tasks.py:39-43
Description: `DELETE /tasks/<id>` não verifica se o usuário autenticado é o dono da task ou tem permissão no projeto.
Impact: Usuário autenticado pode deletar tasks de projetos que não pertencem a ele.
Recommendation: Após autenticação, verificar `task.project.owner_id == current_user.id` antes de permitir deleção.

### [MEDIUM] CORS sem Restrição de Origem
File: app.py:7
Description: `CORS(app)` aceita requisições de qualquer origem sem restrição.
Impact: Qualquer site externo pode fazer requisições autenticadas em nome do usuário (CSRF).
Recommendation: `CORS(app, origins=Config.CORS_ORIGINS)` com lista explícita de origens permitidas.

### [LOW] Debug Mode Habilitado em Produção
File: app.py:19
Description: `app.run(debug=True)` habilita o Werkzeug debugger interativo.
Impact: Exposição de stack traces e execução remota de código se acessível externamente.
Recommendation: `app.run(debug=Config.DEBUG)` com `DEBUG=false` em produção.

### [LOW] Função Não Utilizada em utils/helpers.py
File: utils/helpers.py:10-12
Description: `calculate_progress(done, total)` está definida mas nunca importada ou chamada em nenhum módulo do projeto.
Impact: Dead code aumenta o ruído do codebase.
Recommendation: Remover a função ou utilizá-la nos endpoints de summary de projeto.

### [LOW] Magic Strings de Status sem Constante Nomeada
File: services/task_service.py:21-23
Description: Strings `"todo"`, `"in_progress"` e `"done"` usadas inline sem constante nomeada, duplicadas entre `task_service.py` e `models/task.py`.
Impact: Rename de qualquer status requer busca e substituição manual em múltiplos arquivos.
Recommendation: Definir `VALID_STATUSES = frozenset({"todo", "in_progress", "done"})` em `config/settings.py` e importar onde necessário.

================================
Total: 14 findings
================================
