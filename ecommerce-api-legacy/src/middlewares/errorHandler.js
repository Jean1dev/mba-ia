function errorHandler(err, req, res, next) {
    if (err.name === 'ValidationError' || err.message.includes('obrigatório') || err.message.includes('inválid')) {
        return res.status(400).json({ error: err.message });
    }
    if (err.name === 'UnauthorizedError') {
        return res.status(401).json({ error: 'Invalid token' });
    }
    if (err.message === 'Curso não encontrado' || err.message === 'Aluno não encontrado') {
        return res.status(404).json({ error: err.message });
    }
    console.error(err.stack);
    res.status(500).json({ error: 'Internal server error' });
}

module.exports = errorHandler;
