module.exports = {
    jwtSecret: process.env.JWT_SECRET || 'dev-only-change-in-production',
    port: parseInt(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || './lms.db',
    corsOrigins: process.env.CORS_ORIGINS || '*',
    jwtExpiresIn: process.env.JWT_EXPIRES_IN || '7d',
};
