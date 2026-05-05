class CursoModel {
    constructor(db) {
        this.db = db;
    }

    findAll() {
        return this.db.prepare('SELECT * FROM cursos').all();
    }

    findById(id) {
        return this.db.prepare('SELECT * FROM cursos WHERE id = ?').get(id) || null;
    }

    insert(data) {
        const stmt = this.db.prepare(
            'INSERT INTO cursos (titulo, descricao, preco, instrutor, vagas) VALUES (?, ?, ?, ?, ?)'
        );
        const result = stmt.run(data.titulo, data.descricao, data.preco, data.instrutor, data.vagas || 30);
        return this.findById(result.lastInsertRowid);
    }

    decrementVagas(cursoId) {
        this.db.prepare('UPDATE cursos SET vagas = vagas - 1 WHERE id = ?').run(cursoId);
    }
}

module.exports = CursoModel;
