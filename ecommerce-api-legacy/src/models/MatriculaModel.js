class MatriculaModel {
    constructor(db) {
        this.db = db;
    }

    findByAluno(alunoId) {
        return this.db.prepare(`
            SELECT m.*, c.titulo as curso_titulo, c.preco as curso_preco, c.instrutor
            FROM matriculas m
            JOIN cursos c ON c.id = m.curso_id
            WHERE m.aluno_id = ?
        `).all(alunoId);
    }

    findDuplicate(alunoId, cursoId) {
        return this.db.prepare(
            'SELECT id FROM matriculas WHERE aluno_id = ? AND curso_id = ? AND status = ?'
        ).get(alunoId, cursoId, 'ativo');
    }

    insert(alunoId, cursoId, valorPago) {
        const result = this.db.prepare(
            'INSERT INTO matriculas (aluno_id, curso_id, status, pago, valor_pago) VALUES (?, ?, ?, ?, ?)'
        ).run(alunoId, cursoId, 'ativo', 1, valorPago);
        return result.lastInsertRowid;
    }

    insertPagamento(matriculaId, valor, metodo) {
        this.db.prepare(
            'INSERT INTO pagamentos (matricula_id, valor, metodo, status) VALUES (?, ?, ?, ?)'
        ).run(matriculaId, valor, metodo, 'aprovado');
    }
}

module.exports = MatriculaModel;
