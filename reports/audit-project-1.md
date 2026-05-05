================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~381 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials / Secret Key
File: app.py:13
Description: `SECRET_KEY` hardcoded como string literal `"minha-chave-super-secreta-123"` diretamente no código-fonte. O mesmo valor é duplicado em `models.py:88` como `JWT_SECRET`.
Impact: Qualquer pessoa com acesso ao repositório conhece a chave secreta da aplicação. Comprometimento total de sessões e tokens.
Recommendation: Carregar de variável de ambiente via `os.environ.get("SECRET_KEY")`. Criar `config/settings.py` com classe `Config`.

### [CRITICAL] SQL Injection — Concatenação de String em Query
File: models.py:38
Description: Query SQL construída com concatenação direta: `"SELECT * FROM produtos WHERE id = " + str(produto_id)`. Qualquer valor passado como `produto_id` é executado como SQL.
Impact: Permite extração, modificação ou deleção de qualquer dado no banco de dados.
Recommendation: Usar query parametrizada: `cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))`.

### [CRITICAL] SQL Injection — f-string Interpolation
File: models.py:101
Description: Query construída com f-string: `f"SELECT * FROM usuarios WHERE email = '{email}'"`. O valor de `email` é inserido diretamente na string SQL.
Impact: SQL Injection clássico — atacante pode autenticar como qualquer usuário ou extrair toda a base.
Recommendation: `conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,))`.

### [CRITICAL] Senha Armazenada com MD5 sem Salt (Algoritmo Quebrado)
File: models.py:116, models.py:138
Description: Senhas hasheadas apenas com `hashlib.md5(senha.encode()).hexdigest()`. MD5 é considerado criptograficamente quebrado para armazenamento de senhas e não usa salt.
Impact: Rainbow table attacks triviais. Senhas expostas em caso de vazamento do banco de dados.
Recommendation: Usar `bcrypt.hashpw(senha.encode(), bcrypt.gensalt())` para hash e `bcrypt.checkpw` para verificação.

### [HIGH] God Class — models.py Contém 4 Domínios + Lógica de Negócio
File: models.py:1-212
Description: Arquivo único com 212 linhas contendo acesso a dados, validação de negócio, lógica de checkout e formatação para 4 domínios: Produto, Usuário, Pedido, ItensPedido.
Impact: Impossível testar classes em isolamento. Qualquer mudança em um domínio pode quebrar outro. Alta dificuldade de manutenção.
Recommendation: Separar em `models/produto_model.py`, `models/usuario_model.py`, `models/pedido_model.py` — cada um com única responsabilidade de acesso a dados.

### [HIGH] Lógica de Negócio Pesada no Model (Violação MVC)
File: models.py:142-188 (PedidoModel.criar_pedido)
Description: Toda regra de checkout — validação de estoque, cálculo de total, criação de itens e atualização de estoque — está no `PedidoModel`, que deveria apenas acessar dados.
Impact: Models com lógica de negócio são impossíveis de testar sem banco de dados. Acoplamento alto.
Recommendation: Mover regras de negócio para um `PedidoController` ou `CheckoutService`.

### [HIGH] Dados Sensíveis (Senhas) Expostos na Resposta da API
File: controllers.py:37-39 (get_usuarios)
Description: A rota `GET /usuarios` executa `SELECT id, nome, email, senha, admin FROM usuarios` e retorna o campo `senha` (hash MD5) para qualquer requisição não autenticada.
Impact: Exposição de todos os hashes de senha sem autenticação. Com MD5, qualquer hash pode ser quebrado por rainbow table.
Recommendation: Excluir `senha` do SELECT em `find_all()`. Retornar apenas `id, nome, email, admin`.

### [HIGH] Ausência de Autenticação em Rotas Protegidas
File: controllers.py:36, controllers.py:69-71, app.py:21-30
Description: Rotas `DELETE /produtos/<id>`, `PUT /produtos/<id>` e `POST /pedidos` não verificam autenticação. Qualquer usuário anônimo pode modificar produtos ou criar pedidos em nome de outros usuários.
Impact: Qualquer pessoa pode deletar todos os produtos ou criar pedidos fraudulentos.
Recommendation: Implementar middleware de autenticação `@require_auth` e aplicar nas rotas sensíveis.

### [HIGH] Token de Autenticação Falso sem JWT Real
File: controllers.py:64
Description: Login retorna `f"fake-token-{usuario['id']}-{usuario['email']}"` — um token previsível e não verificável, sem expiração, sem assinatura criptográfica.
Impact: Qualquer pessoa que conheça o ID e email de um usuário pode forjar seu token.
Recommendation: Implementar JWT real com `PyJWT` ou usar `secrets.token_hex(32)` com armazenamento server-side.

### [MEDIUM] N+1 Query Problem em get_all()
File: models.py:18-30
Description: Para cada produto retornado pelo primeiro SELECT, uma nova conexão ao banco é aberta para buscar o `total_vendas`. Para 100 produtos, isso gera 101 queries.
Impact: Degradação severa de performance com volume de dados real.
Recommendation: Usar `LEFT JOIN` com `COUNT()` em query única: `SELECT p.*, COUNT(i.id) as total_vendas FROM produtos p LEFT JOIN itens_pedido i ON i.produto_id = p.id GROUP BY p.id`.

### [MEDIUM] Race Condition na Atualização de Estoque
File: models.py:163-167
Description: O `criar_pedido` verifica estoque e depois atualiza em operações separadas sem transação atômica. Em alta concorrência, dois pedidos simultâneos podem ver o mesmo estoque disponível.
Impact: Venda de produtos sem estoque (overselling) em cenários de alta concorrência.
Recommendation: Envolver toda a operação em uma transação `BEGIN TRANSACTION` e usar `UPDATE ... WHERE estoque >= ?`.

### [MEDIUM] CORS Liberado para Qualquer Origem
File: app.py:15
Description: `CORS(app)` sem restrição de origins aceita requisições de qualquer domínio, incluindo sites maliciosos.
Impact: Vulnerabilidade a ataques CSRF e acesso não autorizado de origens desconhecidas.
Recommendation: Configurar `CORS(app, origins=Config.CORS_ORIGINS)` e definir origens permitidas explicitamente.

### [LOW] Debug Mode Habilitado em Produção
File: app.py:37
Description: `app.run(debug=True)` expõe o Werkzeug debugger interativo, permitindo execução de código arbitrário via browser se acessível.
Impact: Execução remota de código arbitrário se o servidor for acessível externamente.
Recommendation: `app.run(debug=Config.DEBUG)` com `DEBUG=false` no ambiente de produção.

### [LOW] Print de Debug com Credenciais Exposto
File: models.py:134
Description: `print(f"[DEBUG] Tentativa de login: {email} / {senha}")` loga email e senha em texto plano nos logs do servidor.
Impact: Credenciais de usuários armazenadas nos logs. Violação de privacidade.
Recommendation: Remover completamente o print. Usar `app.logger.debug` com nível controlável se necessário.

### [LOW] Variáveis com Nomes sem Significado
File: models.py:107-109
Description: Campos de negócio `nome`, `email` e `senha` atribuídos às variáveis `x`, `y`, `z` sem qualquer semântica.
Impact: Código ilegível e de difícil manutenção.
Recommendation: Usar nomes descritivos: `nome = data.get("nome")`, `email = data.get("email")`, `senha = data.get("senha")`.

================================
Total: 15 findings
================================
