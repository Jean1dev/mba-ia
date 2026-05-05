const bcrypt = require('bcrypt');

const SALT_ROUNDS = 10;

class AlunoModel {
    constructor(db) {
        this.db = db;
    }

    findByEmail(email) {
        return this.db.prepare('SELECT * FROM alunos WHERE email = ?').get(email) || null;
    }

    findById(id) {
        return this.db.prepare('SELECT id, nome, email, plano FROM alunos WHERE id = ?').get(id) || null;
    }

    async insert(nome, email, senha) {
        const hash = await bcrypt.hash(senha, SALT_ROUNDS);
        try {
            const result = this.db.prepare(
                'INSERT INTO alunos (nome, email, senha) VALUES (?, ?, ?)'
            ).run(nome, email, hash);
            return this.findById(result.lastInsertRowid);
        } catch (err) {
            if (err.message.includes('UNIQUE constraint')) {
                throw new Error('Email já cadastrado');
            }
            throw err;
        }
    }

    async verifyPassword(plainPassword, hash) {
        return bcrypt.compare(plainPassword, hash);
    }
}

module.exports = AlunoModel;
