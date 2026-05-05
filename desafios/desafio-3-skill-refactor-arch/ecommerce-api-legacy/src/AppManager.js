const sqlite3 = require('sqlite3').verbose();
const { config, logAndCache, badCrypto, totalRevenue } = require('./utils');

class AppManager {
    constructor() {

        this.db = new sqlite3.Database(':memory:');
    }

    initDb() {
        this.db.serialize(() => {
            this.db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
            this.db.run("CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
            this.db.run("CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)");
            this.db.run("CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)");
            this.db.run("CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");
            
            this.db.run("INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')");
            this.db.run("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
            this.db.run("INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)");
            this.db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
        });
    }

    setupRoutes(app) {
        const self = this;

        app.post('/api/checkout', (req, res) => {
            let u = req.body.usr;
            let e = req.body.eml;
            let p = req.body.pwd;
            let cid = req.body.c_id;
            let cc = req.body.card;

            if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");

            this.db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [cid], (err, course) => {
                if (err || !course) return res.status(404).send("Curso não encontrado");

                this.db.get("SELECT id FROM users WHERE email = ?", [e], (err, user) => {
                    if (err) return res.status(500).send("Erro DB");

                    let processPaymentAndEnroll = (userId) => {

                        console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
                        let status = cc.startsWith("4") ? "PAID" : "DENIED";

                        if (status === "DENIED") return res.status(400).send("Pagamento recusado");

                        this.db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [userId, cid], function(err) {
                            if (err) return res.status(500).send("Erro Matrícula");
                            let enrId = this.lastID;

                            self.db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [enrId, course.price, status], function(err) {
                                if (err) return res.status(500).send("Erro Pagamento");

                                self.db.run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [`Checkout curso ${cid} por ${userId}`], (err) => {
                                    
                                    logAndCache(`last_checkout_${userId}`, course.title);
                                    res.status(200).json({ msg: "Sucesso", enrollment_id: enrId });
                                });
                            });
                        });
                    };

                    if (!user) {

                        let hash = badCrypto(p || "123456");
                        this.db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [u, e, hash], function(err) {
                            if (err) return res.status(500).send("Erro ao criar usuário");
                            processPaymentAndEnroll(this.lastID);
                        });
                    } else {
                        processPaymentAndEnroll(user.id);
                    }
                });
            });
        });

        app.get('/api/admin/financial-report', (req, res) => {
            let report = [];

            this.db.all("SELECT * FROM courses", [], (err, courses) => {
                if (err) return res.status(500).send("Erro DB");
                
                let coursesPending = courses.length;
                if (coursesPending === 0) return res.json(report);

                courses.forEach(c => {
                    let courseData = { course: c.title, revenue: 0, students: [] };
                    
                    this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
                        let enrPending = enrollments.length;
                        
                        if (enrPending === 0) {
                            report.push(courseData);
                            coursesPending--;
                            if (coursesPending === 0) res.json(report);
                            return;
                        }

                        enrollments.forEach(enr => {

                            this.db.get("SELECT name, email FROM users WHERE id = ?", [enr.user_id], (err, user) => {
                                
                                this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?", [enr.id], (err, payment) => {
                                    
                                    if (payment && payment.status === 'PAID') {
                                        courseData.revenue += payment.amount;
                                    }
                                    
                                    courseData.students.push({
                                        student: user ? user.name : 'Unknown',
                                        paid: payment ? payment.amount : 0
                                    });

                                    enrPending--;
                                    if (enrPending === 0) {
                                        report.push(courseData);
                                        coursesPending--;
                                        if (coursesPending === 0) res.json(report);
                                    }
                                });
                            });
                        });
                    });
                });
            });
        });

        app.delete('/api/users/:id', (req, res) => {
            let id = req.params.id;
            this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {

                res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
            });
        });
    }
}

module.exports = AppManager;
