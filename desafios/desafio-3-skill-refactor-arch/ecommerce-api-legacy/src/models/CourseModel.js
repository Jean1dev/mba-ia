class CourseModel {
    constructor(db) { this.db = db; }

    findAll() {
        return this.db.prepare('SELECT * FROM courses WHERE active = 1').all();
    }

    findById(id) {
        return this.db.prepare('SELECT * FROM courses WHERE id = ? AND active = 1').get(id) || null;
    }

    getFinancialReport() {
        return this.db.prepare(`
            SELECT c.title,
                   COUNT(e.id)                              AS total_enrollments,
                   COALESCE(SUM(CASE WHEN p.status = 'PAID' THEN p.amount ELSE 0 END), 0) AS revenue,
                   GROUP_CONCAT(u.name)                     AS students
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            GROUP BY c.id, c.title
        `).all();
    }
}

module.exports = CourseModel;
