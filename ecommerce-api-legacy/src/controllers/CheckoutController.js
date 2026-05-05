const CUPONS = {
    DESCONTO10: 0.90,
    DESCONTO20: 0.80,
    METADE: 0.50,
};

class CheckoutController {
    constructor(cursoModel, matriculaModel) {
        this.cursoModel = cursoModel;
        this.matriculaModel = matriculaModel;
    }

    realizarCheckout(alunoId, cursoId, metodoPagamento, cupom) {
        const curso = this.cursoModel.findById(cursoId);
        if (!curso) throw new Error('Curso não encontrado');
        if (curso.vagas <= 0) throw new Error('Curso sem vagas disponíveis');

        const duplicate = this.matriculaModel.findDuplicate(alunoId, cursoId);
        if (duplicate) throw new Error('Aluno já matriculado neste curso');

        const fator = cupom && CUPONS[cupom] ? CUPONS[cupom] : 1;
        const valorFinal = parseFloat((curso.preco * fator).toFixed(2));

        const matriculaId = this.matriculaModel.insert(alunoId, cursoId, valorFinal);
        this.matriculaModel.insertPagamento(matriculaId, valorFinal, metodoPagamento);
        this.cursoModel.decrementVagas(cursoId);

        return {
            sucesso: true,
            matricula_id: matriculaId,
            valor_cobrado: valorFinal,
            curso: curso.titulo,
        };
    }

    getMatriculas(alunoId) {
        return this.matriculaModel.findByAluno(alunoId);
    }
}

module.exports = CheckoutController;
