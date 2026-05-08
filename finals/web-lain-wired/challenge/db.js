const crypto = require('crypto');
const sqlite = require('sqlite-async');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derived = crypto.scryptSync(String(password), salt, 64).toString('hex');
    return `scrypt$${salt}$${derived}`;
}

function verifyPassword(storedPassword, suppliedPassword) {
    const stored = String(storedPassword || '');
    const supplied = String(suppliedPassword || '');

    if (!stored.startsWith('scrypt$')) {
        return stored === supplied;
    }

    const parts = stored.split('$');
    if (parts.length !== 3) {
        return false;
    }

    const [, salt, expectedHex] = parts;
    const derived = crypto.scryptSync(supplied, salt, 64).toString('hex');
    return crypto.timingSafeEqual(Buffer.from(derived, 'hex'), Buffer.from(expectedHex, 'hex'));
}

class Database {
    constructor(filename) {
        this.filename = filename;
        this.db = null;
    }

    async connect() {
        this.db = await sqlite.open(this.filename);
    }

    async migrate() {
        await this.db.exec(`
            PRAGMA journal_mode = WAL;

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                otp_code TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                css TEXT NOT NULL,
                publish_key TEXT,
                review_revision TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                submission_id INTEGER NOT NULL,
                request_path TEXT NOT NULL,
                source_ip TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        `);

        const submissionColumns = await this.db.all('PRAGMA table_info(submissions)');
        if (!submissionColumns.some((column) => column.name === 'publish_key')) {
            if (submissionColumns.some((column) => column.name === 'review_code')) {
                await this.db.exec('ALTER TABLE submissions RENAME COLUMN review_code TO publish_key');
            } else {
                await this.db.exec('ALTER TABLE submissions ADD COLUMN publish_key TEXT');
            }
        }
        if (!submissionColumns.some((column) => column.name === 'review_revision')) {
            await this.db.exec('ALTER TABLE submissions ADD COLUMN review_revision TEXT');
        }

        await this.db.run(
            `UPDATE submissions
             SET publish_key = lower(hex(randomblob(8)))
             WHERE publish_key IS NULL OR publish_key = ''`
        );
        await this.db.run(
            `UPDATE submissions
             SET review_revision = lower(hex(randomblob(5)))
             WHERE review_revision IS NULL OR review_revision = ''`
        );

        const telemetryColumns = await this.db.all("PRAGMA table_info(telemetry)");
        if (!telemetryColumns.length) {
            const leakColumns = await this.db.all("PRAGMA table_info(leaks)");
            if (leakColumns.length) {
                await this.db.exec('ALTER TABLE leaks RENAME TO telemetry');
            }
        }
        const updatedTelemetryColumns = await this.db.all("PRAGMA table_info(telemetry)");
        if (updatedTelemetryColumns.some((column) => column.name === 'position')) {
            await this.db.exec(`
                CREATE TABLE telemetry_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    submission_id INTEGER NOT NULL,
                    request_path TEXT NOT NULL,
                    source_ip TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            `);
            if (updatedTelemetryColumns.some((column) => column.name === 'key_fragment')) {
                await this.db.exec(`
                    INSERT INTO telemetry_new (id, user_id, submission_id, request_path, source_ip, created_at)
                    SELECT
                        id,
                        user_id,
                        submission_id,
                        '/pulse?legacy=1&submission=' || submission_id || '&pos=' || position || '&char=' || key_fragment,
                        source_ip,
                        created_at
                    FROM telemetry;
                `);
            }
            await this.db.exec('DROP TABLE telemetry');
            await this.db.exec('ALTER TABLE telemetry_new RENAME TO telemetry');
        }
    }

    async getUserByCredentials(username, password) {
        const user = await this.db.get(
            'SELECT id, username, password FROM users WHERE username = ?',
            [String(username)]
        );
        if (!user || !verifyPassword(user.password, password)) {
            return null;
        }

        return {
            id: user.id,
            username: user.username
        };
    }

    async getUserByUsername(username) {
        return this.db.get(
            'SELECT id, username FROM users WHERE username = ?',
            [String(username)]
        );
    }

    async getUserById(id) {
        return this.db.get(
            'SELECT id, username, otp_code FROM users WHERE id = ?',
            [Number(id)]
        );
    }

    async createSubmission(userId, css) {
        const publishKey = crypto.randomBytes(8).toString('hex');
        const reviewRevision = crypto.randomBytes(5).toString('hex');
        const result = await this.db.run(
            'INSERT INTO submissions (user_id, css, publish_key, review_revision) VALUES (?, ?, ?, ?)',
            [Number(userId), String(css), publishKey, reviewRevision]
        );
        return result.lastID;
    }

    async createUser(username, password) {
        const otpCode = crypto.randomInt(0, 10000).toString().padStart(4, '0');
        const result = await this.db.run(
            'INSERT INTO users (username, password, otp_code) VALUES (?, ?, ?)',
            [String(username), hashPassword(password), otpCode]
        );

        return {
            id: result.lastID,
            username: String(username),
            otpCode
        };
    }

    async getSubmission(id) {
        return this.db.get(
            `SELECT submissions.id, submissions.user_id, submissions.css, submissions.publish_key, submissions.review_revision,
                    submissions.status, submissions.created_at,
                    users.username
             FROM submissions
             JOIN users ON users.id = submissions.user_id
             WHERE submissions.id = ?`,
            [Number(id)]
        );
    }

    async getSubmissionCss(id) {
        return this.db.get(
            'SELECT css FROM submissions WHERE id = ?',
            [Number(id)]
        );
    }

    async listSubmissionsByUser(userId) {
        return this.db.all(
            `SELECT id, status, created_at
             FROM submissions
             WHERE user_id = ?
             ORDER BY id DESC`,
            [Number(userId)]
        );
    }

    async addTelemetry(userId, submissionId, requestPath, sourceIp) {
        await this.db.run(
            `INSERT INTO telemetry (user_id, submission_id, request_path, source_ip)
             VALUES (?, ?, ?, ?)`,
            [
                Number(userId),
                Number(submissionId),
                String(requestPath),
                String(sourceIp)
            ]
        );
    }

    async getTelemetryByUser(userId) {
        return this.db.all(
            `SELECT submission_id, request_path, source_ip, created_at
             FROM telemetry
             WHERE user_id = ?
             ORDER BY id DESC`,
            [Number(userId)]
        );
    }

    async markSubmissionApproved(id) {
        await this.db.run(
            `UPDATE submissions SET status = 'approved' WHERE id = ?`,
            [Number(id)]
        );
    }
}

module.exports = Database;
