class CursoController {
    constructor(cursoModel) {
        this.cursoModel = cursoModel;
    }

    listCursos() {
        return this.cursoModel.findAll();
    }

    getCurso(id) {
        const curso = this.cursoModel.findById(id);
        if (!curso) throw new Error('Curso não encontrado');
        return curso;
    }

    createCurso(data) {
        if (!data.titulo || !data.preco) {
            throw new Error('titulo e preco são obrigatórios');
        }
        if (data.preco <= 0) {
            throw new Error('preco deve ser positivo');
        }
        return this.cursoModel.insert(data);
    }
}

module.exports = CursoController;
