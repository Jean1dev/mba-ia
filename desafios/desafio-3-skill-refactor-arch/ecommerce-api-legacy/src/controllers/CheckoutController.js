class CheckoutController {
    constructor(courseModel, userModel, enrollmentModel) {
        this.courseModel = courseModel;
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
    }

    async checkout(body) {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card } = body;

        if (!name || !email || !courseId || !card) {
            throw Object.assign(new Error('Campos obrigatórios: usr, eml, c_id, card'), { status: 400 });
        }

        const course = this.courseModel.findById(courseId);
        if (!course) throw Object.assign(new Error('Curso não encontrado'), { status: 404 });

        let user = this.userModel.findByEmail(email);
        if (!user) {
            user = await this.userModel.insert(name, email, password || '123456');
        }

        if (this.enrollmentModel.findDuplicate(user.id, courseId)) {
            throw Object.assign(new Error('Aluno já matriculado neste curso'), { status: 400 });
        }

        const paymentStatus = card.startsWith('4') ? 'PAID' : 'DENIED';
        if (paymentStatus === 'DENIED') {
            throw Object.assign(new Error('Pagamento recusado'), { status: 400 });
        }

        const enrollmentId = this.enrollmentModel.insert(user.id, courseId);
        this.enrollmentModel.insertPayment(enrollmentId, course.price, paymentStatus);

        return { msg: 'Sucesso', enrollment_id: enrollmentId };
    }

    getFinancialReport() {
        return this.courseModel.getFinancialReport();
    }

    getEnrollments(userId) {
        return this.enrollmentModel.findByUser(userId);
    }

    async deleteUser(userId) {
        this.enrollmentModel.deletePaymentsByUser(userId);
        this.enrollmentModel.deleteByUser(userId);
        return { message: 'Usuário e registros relacionados removidos' };
    }
}

module.exports = CheckoutController;
