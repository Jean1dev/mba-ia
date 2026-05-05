// CRITICAL: God Class - gerencia banco de dados, autenticação, lógica de negócio e cache em um único lugar
const Database = require('better-sqlite3');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const path = require('path');

// CRITICAL: SECRET hardcoded no código-fonte
const JWT_SECRET = 'lms-secret-key-nao-mude-isso';
const DB_PATH = path.join(__dirname, '..', 'lms.db');

class AppManager {
    constructor() {
        this.db = new Database(DB_PATH);
        // HIGH: cache em memória sem TTL nem invalidação
        this.cache = {};
        this._initDB();
    }

    _initDB() {
        this.db.exec(`
            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                preco REAL NOT NULL,
                instrutor TEXT,
                vagas INTEGER DEFAULT 30
            );
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                plano TEXT DEFAULT 'free'
            );
            CREATE TABLE IF NOT EXISTS matriculas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                curso_id INTEGER NOT NULL,
                status TEXT DEFAULT 'ativo',
                pago INTEGER DEFAULT 0,
                valor_pago REAL,
                data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS pagamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula_id INTEGER NOT NULL,
                valor REAL NOT NULL,
                metodo TEXT,
                status TEXT DEFAULT 'pendente',
                data_pagamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            INSERT OR IGNORE INTO cursos (titulo, descricao, preco, instrutor, vagas) VALUES
                ('Python para Data Science', 'Aprenda Python do zero', 299.90, 'Prof. Ana', 30),
                ('JavaScript Avançado', 'ES6+ e frameworks modernos', 399.90, 'Prof. Carlos', 25),
                ('Machine Learning na Prática', 'ML com scikit-learn', 599.90, 'Prof. Maria', 20);
            INSERT OR IGNORE INTO alunos (nome, email, senha, plano) VALUES
                ('Admin LMS', 'admin@lms.com', '$2b$10$fixedhashfortest1234567890123456789012', 'admin'),
                ('Aluno Teste', 'aluno@test.com', '$2b$10$fixedhashfortest1234567890123456789012', 'premium');
        `);
    }

    // HIGH: método único fazendo autenticação, validação e resposta HTTP (deveria ser separado)
    autenticar(email, senha) {
        // CRITICAL: SQL concatenado sem prepared statement em parte do método
        const aluno = this.db.prepare(`SELECT * FROM alunos WHERE email = ?`).get(email);
        if (!aluno) return null;

        // LOW: comparação de senha sem constante de tempo (timing attack)
        const senhaOk = bcrypt.compareSync(senha, aluno.senha);
        if (!senhaOk) return null;

        const token = jwt.sign({ id: aluno.id, email: aluno.email, plano: aluno.plano }, JWT_SECRET, {
            // LOW: expiração hardcoded como string mágica
            expiresIn: '7d'
        });

        return { token, aluno: { id: aluno.id, nome: aluno.nome, email: aluno.email, plano: aluno.plano } };
    }

    verificarToken(token) {
        try {
            return jwt.verify(token, JWT_SECRET);
        } catch {
            return null;
        }
    }

    // HIGH: toda regra de checkout no manager (sem separação de camadas)
    realizarCheckout(alunoId, cursoId, metodoPagamento, cupom) {
        const curso = this.db.prepare('SELECT * FROM cursos WHERE id = ?').get(cursoId);
        if (!curso) return { error: 'Curso não encontrado' };

        // MEDIUM: sem verificação de vagas em transação (race condition)
        if (curso.vagas <= 0) return { error: 'Curso sem vagas disponíveis' };

        // HIGH: lógica de cupom inline sem abstração
        let valorFinal = curso.preco;
        if (cupom === 'DESCONTO10') valorFinal = valorFinal * 0.9;
        else if (cupom === 'DESCONTO20') valorFinal = valorFinal * 0.8;
        else if (cupom === 'METADE') valorFinal = valorFinal * 0.5;

        // MEDIUM: sem verificar duplicidade de matrícula antes de inserir
        const stmt = this.db.prepare(
            'INSERT INTO matriculas (aluno_id, curso_id, status, pago, valor_pago) VALUES (?, ?, ?, ?, ?)'
        );
        const result = stmt.run(alunoId, cursoId, 'ativo', 1, valorFinal);

        this.db.prepare(
            'INSERT INTO pagamentos (matricula_id, valor, metodo, status) VALUES (?, ?, ?, ?)'
        ).run(result.lastInsertRowid, valorFinal, metodoPagamento, 'aprovado');

        this.db.prepare('UPDATE cursos SET vagas = vagas - 1 WHERE id = ?').run(cursoId);

        // HIGH: cache não invalidado após mudança de dados
        this.cache['cursos'] = null;

        return {
            sucesso: true,
            matricula_id: result.lastInsertRowid,
            valor_cobrado: valorFinal,
            curso: curso.titulo
        };
    }

    getCursos() {
        // HIGH: cache sem TTL - dados podem ficar obsoletos indefinidamente
        if (this.cache['cursos']) return this.cache['cursos'];
        const cursos = this.db.prepare('SELECT * FROM cursos').all();
        this.cache['cursos'] = cursos;
        return cursos;
    }

    getCurso(id) {
        return this.db.prepare('SELECT * FROM cursos WHERE id = ?').get(id);
    }

    criarCurso(data) {
        // MEDIUM: sem validação de schema/tipos dos dados
        const stmt = this.db.prepare(
            'INSERT INTO cursos (titulo, descricao, preco, instrutor, vagas) VALUES (?, ?, ?, ?, ?)'
        );
        const result = stmt.run(data.titulo, data.descricao, data.preco, data.instrutor, data.vagas || 30);
        return this.getCurso(result.lastInsertRowid);
    }

    getMatriculasAluno(alunoId) {
        // MEDIUM: N+1 query - busca detalhes do curso para cada matrícula
        const matriculas = this.db.prepare('SELECT * FROM matriculas WHERE aluno_id = ?').all(alunoId);
        return matriculas.map(m => {
            const curso = this.db.prepare('SELECT titulo, preco FROM cursos WHERE id = ?').get(m.curso_id);
            return { ...m, curso };
        });
    }

    registrarAluno(nome, email, senha) {
        // LOW: sem validação de formato de email
        const hash = bcrypt.hashSync(senha, 10);
        try {
            const stmt = this.db.prepare('INSERT INTO alunos (nome, email, senha) VALUES (?, ?, ?)');
            const result = stmt.run(nome, email, hash);
            return { id: result.lastInsertRowid, nome, email };
        } catch (err) {
            // LOW: erro de banco exposto diretamente para o cliente
            return { error: err.message };
        }
    }
}

module.exports = new AppManager();
