const express = require('express');

function createCursosRouter(cursoController) {
    const router = express.Router();

    router.get('/cursos', (req, res, next) => {
        try {
            res.json(cursoController.listCursos());
        } catch (err) {
            next(err);
        }
    });

    router.get('/cursos/:id', (req, res, next) => {
        try {
            res.json(cursoController.getCurso(parseInt(req.params.id)));
        } catch (err) {
            next(err);
        }
    });

    router.post('/cursos', (req, res, next) => {
        try {
            const curso = cursoController.createCurso(req.body || {});
            res.status(201).json(curso);
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = { createCursosRouter };
