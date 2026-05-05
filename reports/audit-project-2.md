================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18.2
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 6 | MEDIUM: 4 | LOW: 4

## Findings

### [CRITICAL] Hardcoded JWT Secret
File: src/AppManager.js:8
Description: `const JWT_SECRET = 'lms-secret-key-nao-mude-isso'` hardcoded no código-fonte da aplicação. Qualquer pessoa com acesso ao repositório pode forjar tokens JWT válidos para qualquer usuário.
Impact: Comprometimento total da autenticação. Atacante pode se autenticar como qualquer aluno ou admin sem conhecer credenciais.
Recommendation: Carregar de `process.env.JWT_SECRET`. Criar `src/config/settings.js` com todas as configurações externalizadas.

### [CRITICAL] God Class — AppManager.js Concentra Todo o Sistema
File: src/AppManager.js:1-135
Description: Classe única com 135 linhas que gerencia: conexão e schema do banco SQLite, autenticação JWT, hashing de senhas, lógica de checkout com cupons, cache em memória, e CRUD de cursos e matrículas.
Impact: Impossível testar qualquer funcionalidade em isolamento. Qualquer bug ou mudança afeta toda a aplicação. Violação completa do Single Responsibility Principle.
Recommendation: Separar em `models/CursoModel.js`, `models/AlunoModel.js`, `models/MatriculaModel.js` e `controllers/AuthController.js`, `controllers/CheckoutController.js`.

### [CRITICAL] Algoritmo JWT sem Especificação Explícita (Deprecated Default)
File: src/AppManager.js:55
Description: `jwt.sign(payload, JWT_SECRET, { expiresIn: '7d' })` não especifica o algoritmo `algorithm: 'HS256'`. Versões antigas do jsonwebtoken aceitam `alg: none` se o padrão mudar, abrindo vetor de ataque.
Impact: Vulnerabilidade de token forgery se a versão do jsonwebtoken mudar o comportamento padrão. Classificado como deprecated usage pelo OWASP.
Recommendation: Sempre especificar: `jwt.sign(payload, secret, { expiresIn: '7d', algorithm: 'HS256' })` e verificar com `jwt.verify(token, secret, { algorithms: ['HS256'] })`.

### [HIGH] Lógica de Checkout Completa Dentro do AppManager (Violação MVC)
File: src/AppManager.js:72-112
Description: O método `realizarCheckout` do AppManager implementa: validação de curso, controle de vagas, lógica de cupons (3 tipos), inserção de matrícula, inserção de pagamento e atualização de vagas — tudo em um único método de 40 linhas.
Impact: Lógica de negócio misturada com acesso a dados. Impossível testar a lógica de desconto sem banco de dados.
Recommendation: Mover para `CheckoutController.js` com o modelo recebendo apenas operações de dados.

### [HIGH] Auth Token Inline em Cada Rota (DRY Violation)
File: src/app.js:40-42, src/app.js:52-54, src/app.js:60-62
Description: O padrão de extração e verificação de token JWT é duplicado manualmente em 3 rotas: `/checkout` e `/minhas-matriculas`, cada uma com `req.headers.authorization?.replace('Bearer ', '')` + `verificarToken`.
Impact: Se a lógica de auth mudar, precisa ser atualizada em múltiplos lugares. Alto risco de inconsistência.
Recommendation: Criar `middlewares/auth.js` com função `requireAuth` aplicada como middleware nas rotas protegidas.

### [HIGH] Cache em Memória sem TTL nem Invalidação Correta
File: src/AppManager.js:22, src/AppManager.js:114-117
Description: `this.cache = {}` armazena resultados de queries sem tempo de expiração. O método `realizarCheckout` invalida o cache atribuindo `null`, mas `getCursos` verifica `if (this.cache['cursos'])` — então o valor `null` não invalida corretamente.
Impact: Dados de cursos (vagas disponíveis) podem ficar desatualizados indefinidamente após matrículas, causando exibição incorreta de vagas.
Recommendation: Remover cache ou implementar com TTL usando timestamps. Preferir invalidação após writes.

### [HIGH] Ausência de Autenticação na Criação de Cursos
File: src/app.js:47-50
Description: `POST /cursos` não exige autenticação — qualquer usuário não autenticado pode criar cursos na plataforma.
Impact: Usuários anônimos podem poluir a plataforma com cursos falsos ou maliciosos.
Recommendation: Aplicar middleware `requireAuth` e verificar `req.user.plano === 'admin'` antes de permitir criação.

### [HIGH] Exposição de Erro de Banco de Dados ao Cliente
File: src/AppManager.js:130
Description: `return { error: err.message }` retorna a mensagem de erro bruta do SQLite (ex: `UNIQUE constraint failed: alunos.email`) diretamente ao cliente.
Impact: Exposição de detalhes de implementação interna (nomes de tabelas, constraints). Facilita fingerprinting da aplicação.
Recommendation: Mapear erros de banco para mensagens amigáveis: `if (err.message.includes('UNIQUE constraint')) throw new Error('Email já cadastrado')`.

### [MEDIUM] N+1 Query em getMatriculasAluno
File: src/AppManager.js:119-124
Description: Para cada matrícula retornada, uma nova query é executada para buscar detalhes do curso: `matriculas.map(m => { const curso = db.prepare('SELECT ...').get(m.curso_id) })`.
Impact: Para um aluno com 10 matrículas, são executadas 11 queries. Performance degrada linearmente com o número de matrículas.
Recommendation: Usar JOIN: `SELECT m.*, c.titulo, c.preco FROM matriculas m JOIN cursos c ON c.id = m.curso_id WHERE m.aluno_id = ?`.

### [MEDIUM] Race Condition no Controle de Vagas
File: src/AppManager.js:79-81
Description: Verificação de `curso.vagas <= 0` e depois `UPDATE cursos SET vagas = vagas - 1` são operações separadas sem transação. Em requisições concorrentes, dois alunos podem passar pela verificação simultaneamente.
Impact: Matriculação acima da capacidade máxima do curso (overselling de vagas).
Recommendation: Usar `BEGIN TRANSACTION` ou `UPDATE cursos SET vagas = vagas - 1 WHERE id = ? AND vagas > 0` e verificar `changes > 0`.

### [MEDIUM] Sem Verificação de Matrícula Duplicada
File: src/AppManager.js:88-91
Description: `realizarCheckout` não verifica se o aluno já está matriculado no curso antes de criar nova matrícula. Um aluno pode pagar pelo mesmo curso múltiplas vezes.
Impact: Cobranças duplicadas e registros inconsistentes de matrículas.
Recommendation: Verificar `SELECT id FROM matriculas WHERE aluno_id = ? AND curso_id = ? AND status = 'ativo'` antes de inserir.

### [MEDIUM] Sem Validação de Entrada nas Rotas
File: src/app.js:30-35, src/app.js:43-50
Description: Rotas `POST /auth/login`, `POST /auth/register` e `POST /checkout` não validam campos obrigatórios antes de chamar o AppManager. Campos undefined passam diretamente para queries SQL.
Impact: Erros internos não controlados, mensagens de erro confusas para o cliente, possível comportamento inesperado.
Recommendation: Validar presença e tipos dos campos antes de chamar controllers.

### [LOW] Estado Global Mutável Compartilhado (utils.js)
File: src/utils.js:7-8
Description: `let activeUsers = {}` e `let sessionStore = {}` são objetos mutáveis em escopo de módulo. Em ambiente multi-worker (cluster), cada worker teria seu próprio estado, causando inconsistência.
Impact: Em produção com múltiplos workers, sessões ficam invisíveis entre processos.
Recommendation: Remover ou substituir por armazenamento externo (Redis). Se single-process, pelo menos encapsular em classe.

### [LOW] Porta Hardcoded sem Variável de Ambiente
File: src/app.js:72
Description: `const PORT = 3000` hardcoded sem fallback para `process.env.PORT`.
Impact: Impossível configurar a porta sem editar o código-fonte. Problemas em ambientes de deploy (Heroku, Railway, etc.) que atribuem porta via env var.
Recommendation: `const PORT = parseInt(process.env.PORT) || 3000`.

### [LOW] Função Não Utilizada (Dead Code)
File: src/utils.js:23-25
Description: Função `slugify(text)` definida mas nunca importada ou chamada em nenhum outro arquivo.
Impact: Código morto aumenta ruído e confunde novos desenvolvedores.
Recommendation: Remover a função.

### [LOW] Magic Strings de Cupom sem Constante Nomeada
File: src/AppManager.js:83-87
Description: Valores de cupom `'DESCONTO10'`, `'DESCONTO20'`, `'METADE'` e seus fatores `0.9`, `0.8`, `0.5` hardcoded inline sem constantes nomeadas ou configuração externa.
Impact: Para adicionar ou modificar um cupom, é preciso alterar a lógica de negócio diretamente. Sem visibilidade dos cupons disponíveis.
Recommendation: Definir mapa de cupons como constante: `const CUPONS = { DESCONTO10: 0.90, DESCONTO20: 0.80, METADE: 0.50 }`.

================================
Total: 17 findings
================================
