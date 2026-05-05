const express = require('express');

function createCoursesRouter(courseModel) {
    const router = express.Router();

    router.get('/api/courses', (req, res, next) => {
        try {
            res.json(courseModel.findAll());
        } catch (err) { next(err); }
    });

    router.get('/api/courses/:id', (req, res, next) => {
        try {
            const course = courseModel.findById(parseInt(req.params.id));
            if (!course) return res.status(404).json({ error: 'Curso não encontrado' });
            res.json(course);
        } catch (err) { next(err); }
    });

    return router;
}

module.exports = { createCoursesRouter };
