const bcrypt = require('bcrypt');
const SALT_ROUNDS = 10;

class UserModel {
    constructor(db) { this.db = db; }

    findByEmail(email) {
        return this.db.prepare('SELECT * FROM users WHERE email = ?').get(email) || null;
    }

    findById(id) {
        return this.db.prepare('SELECT id, name, email FROM users WHERE id = ?').get(id) || null;
    }

    async insert(name, email, password) {
        const hash = await bcrypt.hash(password, SALT_ROUNDS);
        try {
            const result = this.db.prepare(
                'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)'
            ).run(name, email, hash);
            return this.findById(result.lastInsertRowid);
        } catch (err) {
            if (err.message.includes('UNIQUE')) throw new Error('Email já cadastrado');
            throw err;
        }
    }

    async verifyPassword(plain, hash) {
        return bcrypt.compare(plain, hash);
    }
}

module.exports = UserModel;
