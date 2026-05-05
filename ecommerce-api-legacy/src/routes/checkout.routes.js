const express = require('express');

function createCheckoutRouter(checkoutController, requireAuth) {
    const router = express.Router();

    router.post('/checkout', requireAuth, (req, res, next) => {
        try {
            const { curso_id, metodo_pagamento, cupom } = req.body || {};
            if (!curso_id || !metodo_pagamento) {
                return res.status(400).json({ error: 'curso_id e metodo_pagamento são obrigatórios' });
            }
            const result = checkoutController.realizarCheckout(
                req.user.id, curso_id, metodo_pagamento, cupom
            );
            res.json(result);
        } catch (err) {
            next(err);
        }
    });

    router.get('/minhas-matriculas', requireAuth, (req, res, next) => {
        try {
            res.json(checkoutController.getMatriculas(req.user.id));
        } catch (err) {
            next(err);
        }
    });

    return router;
}

module.exports = { createCheckoutRouter };
