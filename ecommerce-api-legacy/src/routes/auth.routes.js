const express = require('express');

function createAuthRouter(authController) {
    const router = express.Router();

    router.post('/auth/login', async (req, res, next) => {
        try {
            const { email, senha } = req.body || {};
            const result = await authController.login(email, senha);
            res.json(result);
        } catch (err) {
            next(err);
        }
    });

    router.post('/auth/register', async (req, res, next) => {
        try {
            const { nome, email, senha } = req.body || {};
            const aluno = await authController.register(nome, email, senha);
            res.status(201).json(aluno);
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = { createAuthRouter };
