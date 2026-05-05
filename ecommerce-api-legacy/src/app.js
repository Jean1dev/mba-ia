const express = require('express');
const cors = require('cors');
const config = require('./config/settings');
const { getDB } = require('./database');

const CursoModel = require('./models/CursoModel');
const AlunoModel = require('./models/AlunoModel');
const MatriculaModel = require('./models/MatriculaModel');

const AuthController = require('./controllers/AuthController');
const CursoController = require('./controllers/CursoController');
const CheckoutController = require('./controllers/CheckoutController');

const { createAuthMiddleware } = require('./middlewares/auth');
const errorHandler = require('./middlewares/errorHandler');

const { createAuthRouter } = require('./routes/auth.routes');
const { createCursosRouter } = require('./routes/cursos.routes');
const { createCheckoutRouter } = require('./routes/checkout.routes');

function createApp() {
    const app = express();
    app.use(cors({ origin: config.corsOrigins }));
    app.use(express.json());

    const db = getDB();

    const cursoModel = new CursoModel(db);
    const alunoModel = new AlunoModel(db);
    const matriculaModel = new MatriculaModel(db);

    const authController = new AuthController(alunoModel);
    const cursoController = new CursoController(cursoModel);
    const checkoutController = new CheckoutController(cursoModel, matriculaModel);

    const requireAuth = createAuthMiddleware(authController);

    app.use(createAuthRouter(authController));
    app.use(createCursosRouter(cursoController));
    app.use(createCheckoutRouter(checkoutController, requireAuth));

    app.use(errorHandler);

    return app;
}

const app = createApp();

if (require.main === module) {
    app.listen(config.port, () => {
        console.log(`LMS API running on port ${config.port}`);
    });
}

module.exports = app;
