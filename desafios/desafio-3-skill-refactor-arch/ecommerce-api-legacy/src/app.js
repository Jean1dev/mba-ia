const express = require('express');
const config = require('./config/settings');
const { getDB } = require('./database');

const UserModel = require('./models/UserModel');
const CourseModel = require('./models/CourseModel');
const EnrollmentModel = require('./models/EnrollmentModel');
const CheckoutController = require('./controllers/CheckoutController');

const { createCheckoutRouter } = require('./routes/checkout.routes');
const { createCoursesRouter } = require('./routes/courses.routes');
const errorHandler = require('./middlewares/errorHandler');

function createApp() {
    const app = express();
    app.use(express.json());

    const db = getDB();
    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);
    const checkoutController = new CheckoutController(courseModel, userModel, enrollmentModel);

    app.use(createCoursesRouter(courseModel));
    app.use(createCheckoutRouter(checkoutController));
    app.get('/health', (req, res) => res.json({ status: 'ok' }));
    app.use(errorHandler);
    return app;
}

const app = createApp();

if (require.main === module) {
    app.listen(config.port, () => {
        console.log(`LMS API rodando na porta ${config.port}`);
    });
}

module.exports = app;
