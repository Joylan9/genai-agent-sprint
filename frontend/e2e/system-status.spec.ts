import { test, expect } from '@playwright/test';
import fs from 'fs';

const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': '*'
};

test.describe('System Health Monitoring UI', () => {
    test.beforeEach(async ({ page }) => {
        page.on('request', req => console.log('>>', req.method(), req.url()));
        page.on('response', res => console.log('<<', res.status(), res.url()));

        await page.route('**/health', async route => {
            if (route.request().method() === 'OPTIONS') {
                await route.fulfill({ status: 204, headers: corsHeaders });
                return;
            }
            await route.fulfill({ json: { status: 'ok', model: 'llama2' }, headers: corsHeaders });
        });

        await page.route('**/ready', async route => {
            if (route.request().method() === 'OPTIONS') {
                await route.fulfill({ status: 204, headers: corsHeaders });
                return;
            }
            await route.fulfill({ json: { status: 'ready', checks: { mongodb: 'ready' } }, headers: corsHeaders });
        });

        await page.goto('/status');
    });

    test('should render 4 vital system status cards', async ({ page }) => {
        await page.waitForTimeout(3000); // give it time to load or throw
        const html = await page.content();
        fs.writeFileSync('debug.html', html);

        const cards = page.locator('div.rounded-lg.border.bg-white');
        await expect(cards).toHaveCount(4);
    });
});
