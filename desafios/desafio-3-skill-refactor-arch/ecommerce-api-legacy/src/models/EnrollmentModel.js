class EnrollmentModel {
    constructor(db) { this.db = db; }

    findByUser(userId) {
        return this.db.prepare(`
            SELECT e.*, c.title, c.price, p.status as payment_status, p.amount
            FROM enrollments e
            JOIN courses c ON c.id = e.course_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            WHERE e.user_id = ?
        `).all(userId);
    }

    findDuplicate(userId, courseId) {
        return this.db.prepare(
            'SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?'
        ).get(userId, courseId);
    }

    insert(userId, courseId) {
        const result = this.db.prepare(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)'
        ).run(userId, courseId);
        return result.lastInsertRowid;
    }

    insertPayment(enrollmentId, amount, status) {
        this.db.prepare(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)'
        ).run(enrollmentId, amount, status);
    }

    deleteByUser(userId) {
        this.db.prepare('DELETE FROM enrollments WHERE user_id = ?').run(userId);
    }

    deletePaymentsByUser(userId) {
        this.db.prepare(`
            DELETE FROM payments WHERE enrollment_id IN (
                SELECT id FROM enrollments WHERE user_id = ?
            )
        `).run(userId);
    }
}

module.exports = EnrollmentModel;
