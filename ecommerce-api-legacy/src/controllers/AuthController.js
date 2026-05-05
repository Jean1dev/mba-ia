const jwt = require('jsonwebtoken');
const config = require('../config/settings');

class AuthController {
    constructor(alunoModel) {
        this.alunoModel = alunoModel;
    }

    async login(email, senha) {
        if (!email || !senha) {
            throw new Error('Email e senha são obrigatórios');
        }
        const aluno = this.alunoModel.findByEmail(email);
        if (!aluno) {
            throw new Error('Credenciais inválidas');
        }
        const valid = await this.alunoModel.verifyPassword(senha, aluno.senha);
        if (!valid) {
            throw new Error('Credenciais inválidas');
        }
        const payload = { id: aluno.id, email: aluno.email, plano: aluno.plano };
        const token = jwt.sign(payload, config.jwtSecret, {
            expiresIn: config.jwtExpiresIn,
            algorithm: 'HS256',
        });
        return { token, aluno: { id: aluno.id, nome: aluno.nome, email: aluno.email, plano: aluno.plano } };
    }

    async register(nome, email, senha) {
        if (!nome || !email || !senha) {
            throw new Error('Nome, email e senha são obrigatórios');
        }
        return this.alunoModel.insert(nome, email, senha);
    }

    verifyToken(token) {
        try {
            return jwt.verify(token, config.jwtSecret, { algorithms: ['HS256'] });
        } catch {
            return null;
        }
    }
}

module.exports = AuthController;
