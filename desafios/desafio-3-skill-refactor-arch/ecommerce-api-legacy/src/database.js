const Database = require('better-sqlite3');
const path = require('path');
const config = require('./config/settings');

let db;

function getDB() {
    if (!db) {
        db = new Database(path.resolve(config.dbPath));
        _initSchema(db);
    }
    return db;
}

function _initSchema(db) {
    db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            pass TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            price REAL NOT NULL,
            active INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            enrollment_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'PENDING'
        );
        INSERT OR IGNORE INTO courses (id, title, price, active) VALUES
            (1, 'Clean Architecture', 997.00, 1),
            (2, 'Docker', 497.00, 1);
    `);
}

module.exports = { getDB };
