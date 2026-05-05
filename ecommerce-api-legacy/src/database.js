const Database = require('better-sqlite3');
const path = require('path');
const config = require('./config/settings');

let db;

function getDB() {
    if (!db) {
        db = new Database(path.resolve(config.dbPath));
        initSchema(db);
    }
    return db;
}

function initSchema(db) {
    db.exec(`
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
    `);
}

module.exports = { getDB };
