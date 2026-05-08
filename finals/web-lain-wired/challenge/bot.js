const puppeteer = require('puppeteer');

const browserOptions = {
    headless: true,
    executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/chromium',
    args: [
        '--no-sandbox',
        '--disable-background-networking',
        '--disable-default-apps',
        '--disable-extensions',
        '--disable-gpu',
        '--disable-sync',
        '--disable-translate',
        '--hide-scrollbars',
        '--metrics-recording-only',
        '--mute-audio',
        '--no-first-run',
        '--safebrowsing-disable-auto-update'
    ]
};

async function reviewSubmission({ baseUrl, sessionCookie, submissionId }) {
    const browser = await puppeteer.launch(browserOptions);

    try {
        const page = await browser.newPage();
        await page.setJavaScriptEnabled(false);

        await page.setCookie({
            name: 'session',
            value: sessionCookie,
            url: baseUrl,
            httpOnly: true
        });

        await page.goto(`${baseUrl}/internal/preview/${submissionId}`, {
            waitUntil: 'networkidle2',
            timeout: 7000
        });

        await new Promise((resolve) => setTimeout(resolve, 5000));
    } finally {
        await browser.close();
    }
}

module.exports = { reviewSubmission };
