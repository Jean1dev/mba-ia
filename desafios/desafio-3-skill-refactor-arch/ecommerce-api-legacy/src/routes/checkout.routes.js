const express = require('express');

function createCheckoutRouter(checkoutController) {
    const router = express.Router();

    router.post('/api/checkout', async (req, res, next) => {
        try {
            const result = await checkoutController.checkout(req.body || {});
            res.json(result);
        } catch (err) { next(err); }
    });

    router.get('/api/admin/financial-report', (req, res, next) => {
        try {
            res.json(checkoutController.getFinancialReport());
        } catch (err) { next(err); }
    });

    router.get('/api/users/:id/enrollments', (req, res, next) => {
        try {
            res.json(checkoutController.getEnrollments(parseInt(req.params.id)));
        } catch (err) { next(err); }
    });

    router.delete('/api/users/:id', async (req, res, next) => {
        try {
            const result = await checkoutController.deleteUser(parseInt(req.params.id));
            res.json(result);
        } catch (err) { next(err); }
    });

    return router;
}

module.exports = { createCheckoutRouter };
