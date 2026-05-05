function errorHandler(err, req, res, next) {
    const status = err.status || 500;
    if (status < 500) {
        return res.status(status).json({ error: err.message });
    }
    console.error(err.stack);
    res.status(500).json({ error: 'Internal server error' });
}

module.exports = errorHandler;
