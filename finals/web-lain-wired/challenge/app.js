const crypto = require('crypto');
const path = require('path');
const express = require('express');
const cookieParser = require('cookie-parser');
const jwt = require('jsonwebtoken');
const { graphqlHTTP } = require('express-graphql');
const {
    GraphQLBoolean,
    GraphQLInputObjectType,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString
} = require('graphql');

const Database = require('./db');
const { reviewSubmission } = require('./bot');

const PORT = Number(process.env.PORT || 1337);
const BASE_URL = process.env.BASE_URL || `http://127.0.0.1:${PORT}`;
const FLAG = process.env.FLAG || 'flag{set_flag_env}';
const BODY_LIMIT = process.env.BODY_LIMIT || '8mb';
const MAX_CSS_LENGTH = 50000;
const JWT_SECRET = crypto.randomBytes(32).toString('hex');
const otpRequestWindowMs = 4000;
const otpThrottle = new Map();
const USERNAME_RE = /^[a-z0-9_]{3,24}$/;
const PASSWORD_MIN_LENGTH = 8;
const receiptMarkerKeys = [
    'shadow',
    'stage',
    'body',
    'head',
    'hair',
    'eyeLeft',
    'eyeRight',
    'mouth',
    'neck',
    'jacket',
    'shirt',
    'tie',
    'screen',
    'card',
    'captionLabel',
    'captionName'
];
const revisionMarkerKeys = [
    'proofingState',
    'paletteState',
    'subjectState',
    'cropState',
    'lightingState',
    'contrastState',
    'wardrobeState',
    'deliveryState',
    'archiveState',
    'releaseState'
];

const app = express();
const db = new Database(path.join(__dirname, 'lainwired.db'));

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use('/public', express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: false, limit: BODY_LIMIT }));
app.use(express.json({ limit: BODY_LIMIT }));
app.use(cookieParser());
app.disable('etag');

app.use((req, res, next) => {
    res.setHeader(
        'Content-Security-Policy',
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self'; object-src 'none'; base-uri 'none'"
    );
    next();
});

function signSession(payload) {
    return jwt.sign(payload, JWT_SECRET, { algorithm: 'HS256' });
}

function readSession(req) {
    if (!req.cookies.session) {
        return null;
    }

    try {
        return jwt.verify(req.cookies.session, JWT_SECRET, { algorithms: ['HS256'] });
    } catch {
        return null;
    }
}

function setSession(res, payload) {
    res.cookie('session', signSession(payload), {
        httpOnly: true,
        sameSite: 'lax'
    });
}

function extendSession(res, session, extraFields) {
    setSession(res, {
        ...session,
        ...extraFields
    });
}

function requireLoggedIn(req, res, next) {
    const session = readSession(req);
    if (!session) {
        return res.redirect('/');
    }

    req.sessionUser = session;
    next();
}

function requireVerified(req, res, next) {
    const session = readSession(req);
    if (!session) {
        return res.redirect('/');
    }

    if (!session.verified) {
        return res.redirect('/otp');
    }

    req.sessionUser = session;
    next();
}

function requireAdmin(req, res, next) {
    const session = readSession(req);
    if (!session || session.role !== 'admin') {
        return res.status(403).send('Only the wired can enter this layer.');
    }

    req.sessionUser = session;
    next();
}

function splitValue(value) {
    return value.split('').map((char, index) => ({
        char,
        position: index + 1
    }));
}

function mapValueToKeys(value, keys) {
    const chars = splitValue(value);
    return Object.fromEntries(
        keys.map((key, index) => [key, chars[index]])
    );
}

function canAccessSubmission(session, submission) {
    return Boolean(
        session &&
        submission &&
        (session.role === 'admin' || submission.user_id === session.userId)
    );
}

function getSubmissionIdFromReferrer(referrer) {
    if (!referrer) {
        return 0;
    }

    try {
        const parsed = new URL(referrer);
        const match = parsed.pathname.match(/^\/(?:internal\/preview|preview)\/(\d+)$/);
        if (!match) {
            return 0;
        }
        return Number(match[1]);
    } catch {
        return 0;
    }
}

async function renderDashboard(res, userId, message) {
    const submissions = await db.listSubmissionsByUser(userId);
    res.render('dashboard', {
        page: 'dashboard',
        message,
        submissions,
        logs: []
    });
}

const VerifyResponseType = new GraphQLObjectType({
    name: 'VerifyResponse',
    fields: {
        ok: { type: new GraphQLNonNull(GraphQLBoolean) },
        message: { type: new GraphQLNonNull(GraphQLString) }
    }
});

const PinCheckInputType = new GraphQLInputObjectType({
    name: 'PinCheckInput',
    fields: {
        pin: { type: new GraphQLNonNull(GraphQLString) },
        channel: { type: new GraphQLNonNull(GraphQLString) }
    }
});

const QueryType = new GraphQLObjectType({
    name: 'Query',
    fields: {
        status: {
            type: GraphQLString,
            resolve: () => 'wired'
        }
    }
});

const MutationType = new GraphQLObjectType({
    name: 'Mutation',
    fields: {
        validatePin: {
            type: VerifyResponseType,
            args: {
                input: { type: new GraphQLNonNull(PinCheckInputType) }
            },
            resolve: async (_, { input }, { req, res }) => {
                if (!req.sessionUser) {
                    return {
                        ok: false,
                        message: 'Login first.'
                    };
                }

                if (req.sessionUser.verified) {
                    return {
                        ok: true,
                        message: 'Session already synced.'
                    };
                }

                const user = await db.getUserById(req.sessionUser.userId);
                if (!user) {
                    return {
                        ok: false,
                        message: 'Unknown user.'
                    };
                }

                if (input.channel !== 'editorial') {
                    return {
                        ok: false,
                        message: 'Unsupported sync channel.'
                    };
                }

                if (String(input.pin) === user.otp_code) {
                    setSession(res, {
                        userId: user.id,
                        username: user.username,
                        verified: true,
                        role: 'user'
                    });

                    return {
                        ok: true,
                        message: 'Second factor accepted.'
                    };
                }

                return {
                    ok: false,
                    message: 'OTP mismatch.'
                };
            }
        }
    }
});

const schema = new GraphQLSchema({
    query: QueryType,
    mutation: MutationType
});

app.get('/', (req, res) => {
    const session = readSession(req);
    if (session?.verified) {
        return res.redirect('/dashboard');
    }

    if (session) {
        return res.redirect('/otp');
    }

    res.render('login', {
        error: null,
        registerError: null,
        registeredUsername: null
    });
});

app.post('/login', async (req, res) => {
    const { username = '', password = '' } = req.body;
    const user = await db.getUserByCredentials(username, password);

    if (!user) {
        return res.status(401).render('login', {
            error: 'The wired rejects those credentials.',
            registerError: null,
            registeredUsername: null
        });
    }

    setSession(res, {
        userId: user.id,
        username: user.username,
        verified: false,
        role: 'user'
    });

    res.redirect('/otp');
});

app.post('/register', async (req, res) => {
    const username = String(req.body.username || '').trim().toLowerCase();
    const password = String(req.body.password || '');
    const confirmPassword = String(req.body.confirmPassword || '');
    if (!USERNAME_RE.test(username)) {
        return res.status(400).render('login', {
            error: null,
            registerError: 'Username must be 3-24 chars of lowercase letters, digits, or underscores.',
            registeredUsername: null
        });
    }

    if (password.length < PASSWORD_MIN_LENGTH) {
        return res.status(400).render('login', {
            error: null,
            registerError: 'Password must be at least 8 characters.',
            registeredUsername: null
        });
    }

    if (password !== confirmPassword) {
        return res.status(400).render('login', {
            error: null,
            registerError: 'Password confirmation does not match.',
            registeredUsername: null
        });
    }

    const existingUser = await db.getUserByUsername(username);
    if (existingUser) {
        return res.status(409).render('login', {
            error: null,
            registerError: 'That username already exists.',
            registeredUsername: null
        });
    }

    const createdUser = await db.createUser(username, password);
    return res.status(201).render('login', {
        error: null,
        registerError: null,
        registeredUsername: createdUser.username
    });
});

app.get('/otp', requireLoggedIn, (req, res) => {
    if (req.sessionUser.verified) {
        return res.redirect('/dashboard');
    }

    res.render('otp', { username: req.sessionUser.username });
});

app.post(
    '/graphql',
    requireLoggedIn,
    (req, res, next) => {
        if (req.sessionUser.verified) {
            return next();
        }

        const lastSeen = otpThrottle.get(req.sessionUser.userId) || 0;
        const now = Date.now();
        if (now - lastSeen < otpRequestWindowMs) {
            return res.status(429).json({
                errors: [
                    {
                        message: 'Only one OTP verification request every 4 seconds.'
                    }
                ]
            });
        }

        otpThrottle.set(req.sessionUser.userId, now);
        next();
    },
    graphqlHTTP((req, res) => ({
        schema,
        graphiql: false,
        context: { req, res }
    }))
);

app.get('/dashboard', requireVerified, async (req, res) => {
    await renderDashboard(res, req.sessionUser.userId, req.query.msg || null);
});

app.post('/submit', requireVerified, async (req, res) => {
    const css = String(req.body.css || '').trim();
    if (!css) {
        return renderDashboard(res, req.sessionUser.userId, 'A stylesheet is required.');
    }

    if (css.length > MAX_CSS_LENGTH) {
        return renderDashboard(res, req.sessionUser.userId, 'Stylesheet exceeds the review size limit.');
    }

    const submissionId = await db.createSubmission(req.sessionUser.userId, css);
    const adminCookie = signSession({
        userId: 0,
        username: 'admin',
        verified: true,
        role: 'admin'
    });

    setImmediate(async () => {
        try {
            await reviewSubmission({
                baseUrl: BASE_URL,
                sessionCookie: adminCookie,
                submissionId
            });
        } catch (error) {
            console.error('bot failed', error.message);
        }
    });

    res.redirect(`/dashboard?msg=${encodeURIComponent(`Submission ${submissionId} queued for review. You can preview it from your patch queue.`)}`);
});

app.get('/preview/:id', requireVerified, async (req, res) => {
    const submission = await db.getSubmission(req.params.id);
    if (!submission || submission.user_id !== req.sessionUser.userId) {
        return res.status(404).send('Preview not found.');
    }

    extendSession(res, req.sessionUser, {
        currentSubmissionId: submission.id
    });

    res.render('preview', {
        submission
    });
});

app.get('/submission/:id.css', requireLoggedIn, async (req, res) => {
    const submission = await db.getSubmission(req.params.id);
    if (!submission) {
        return res.status(404).type('text/css').send('/* missing stylesheet */');
    }

    if (!canAccessSubmission(req.sessionUser, submission)) {
        return res.status(403).type('text/css').send('/* denied */');
    }

    res.type('text/css').send(submission.css);
});

app.get('/r', requireLoggedIn, async (req, res) => {
    const submissionId =
        Number(req.sessionUser.currentSubmissionId || 0) ||
        getSubmissionIdFromReferrer(req.get('referer')) ||
        Number(req.query.i || req.query.submission || 0);
    const submission = await db.getSubmission(submissionId);
    if (submission && canAccessSubmission(req.sessionUser, submission)) {
        await db.addTelemetry(
            submission.user_id,
            submission.id,
            req.originalUrl,
            req.ip
        );
    }

    res.status(204).end();
});

app.get('/telemetry', requireVerified, async (req, res) => {
    const logs = await db.getTelemetryByUser(req.sessionUser.userId);
    res.render('dashboard', {
        page: 'logs',
        message: null,
        submissions: [],
        logs
    });
});

app.get('/internal/preview/:id', requireAdmin, async (req, res) => {
    const submission = await db.getSubmission(req.params.id);
    if (!submission) {
        return res.status(404).send('Ghost packet not found.');
    }

    extendSession(res, req.sessionUser, {
        currentSubmissionId: submission.id
    });

    res.render('admin_review', {
        submission,
        receiptMarkers: mapValueToKeys(submission.publish_key, receiptMarkerKeys),
        revisionMarkers: mapValueToKeys(submission.review_revision, revisionMarkerKeys)
    });
});

app.post('/internal/publish', requireVerified, async (req, res) => {
    const submissionId = Number(req.body.submissionId || 0);
    const suppliedReceipt = String(req.body.receipt || '').trim();
    const suppliedRevision = String(req.body.revision || '').trim();
    const submission = await db.getSubmission(submissionId);

    if (!submission || submission.user_id !== req.sessionUser.userId) {
        return res.status(404).send('No such signal.');
    }

    if (suppliedReceipt !== submission.publish_key || suppliedRevision !== submission.review_revision) {
        return res.status(403).send('Release receipt mismatch.');
    }

    await db.markSubmissionApproved(submission.id);
    res.send(`The wired nods back: ${FLAG}`);
});

app.post('/logout', (req, res) => {
    res.clearCookie('session');
    res.redirect('/');
});

app.use((err, req, res, next) => {
    if (err?.type === 'entity.too.large') {
        return res.status(413).send(`Request body too large. Current BODY_LIMIT=${BODY_LIMIT}`);
    }
    return next(err);
});

app.use((_, res) => {
    res.status(404).send('Page not found.');
});

(async () => {
    await db.connect();
    await db.migrate();
    app.listen(PORT, '0.0.0.0', () => {
        console.log(`Listening on ${PORT} with BODY_LIMIT=${BODY_LIMIT}`);
    });
})();
