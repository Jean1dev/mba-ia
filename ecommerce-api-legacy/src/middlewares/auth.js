function createAuthMiddleware(authController) {
    return function requireAuth(req, res, next) {
        const token = (req.headers.authorization || '').replace('Bearer ', '');
        if (!token) {
            return res.status(401).json({ error: 'Authentication required' });
        }
        const user = authController.verifyToken(token);
        if (!user) {
            return res.status(401).json({ error: 'Invalid or expired token' });
        }
        req.user = user;
        next();
    };
}

module.exports = { createAuthMiddleware };
