module.exports = {
    jwtSecret: process.env.JWT_SECRET || 'dev-only-change-in-production',
    port: parseInt(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || './lms.db',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
};
