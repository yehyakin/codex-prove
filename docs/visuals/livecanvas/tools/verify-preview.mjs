import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';

const require = createRequire(import.meta.url);
const {chromium} = require(process.env.LIVECANVAS_PLAYWRIGHT || 'playwright');
const url = process.argv[2];
if (!url?.startsWith('http://127.0.0.1:')) throw new Error('Pass this task\'s loopback preview URL.');
const base = new URL('.', url).href;
const output = 'qa-output/gallery-all';
const series = JSON.parse(await fs.readFile('series.json', 'utf8'));
const ids = Object.values(series).flatMap(entry => entry.ids);
const visibleCount = ids.filter(id => id.endsWith('-zh')).length;
await fs.mkdir(output, {recursive: true});
const browser = await chromium.launch({headless: true, executablePath: process.env.LIVECANVAS_BROWSER});
const issues = [];
const results = [];
try {
  for (const mobile of [false, true]) {
    const context = await browser.newContext({viewport: mobile ? {width: 390, height: 844} : {width: 1440, height: 1080}, reducedMotion: mobile ? 'reduce' : 'no-preference'});
    const page = await context.newPage();
    page.on('pageerror', error => issues.push(error.message));
    page.on('console', message => {if (message.type() === 'error') issues.push(message.text());});
    await page.goto(url, {waitUntil: 'networkidle'});
    assert.equal(await page.locator('article:visible').count(), visibleCount);
    await page.waitForFunction(() => [...document.querySelectorAll('video')].every(v => v.readyState >= 2));
    assert.equal(await page.locator('#motion').isChecked(), !mobile);
    const metadata = await page.locator('video').evaluateAll(videos => videos.map(v => ({id: new URL(v.src).pathname.split('/').at(-2), width: v.videoWidth, height: v.videoHeight, duration: v.duration})));
    assert.deepEqual(metadata.map(video => video.id).sort(), [...ids].sort());
    for (const video of metadata) {
      const render = JSON.parse(await fs.readFile(path.join('out', video.id, 'render.json'), 'utf8'));
      assert.deepEqual(video, {id: video.id, width: render.width, height: render.height, duration: render.durationInFrames / render.fps});
    }
    await page.locator('#motion').check();
    const playing = page.locator('article:visible video');
    const before = await playing.evaluateAll(videos => videos.map(v => v.currentTime));
    await page.waitForTimeout(500);
    const after = await playing.evaluateAll(videos => videos.map(v => v.currentTime));
    after.forEach((time, index) => assert.notEqual(time, before[index], 'Each visible video must advance in the actual browser.'));
    assert.ok(await playing.evaluateAll(videos => videos.every(v => !v.paused)));
    await page.locator('#motion').uncheck();
    assert.equal(await page.locator('body').getAttribute('data-motion'), 'off');
    assert.ok(await page.locator('video').evaluateAll(videos => videos.every(v => v.paused)));
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    await page.screenshot({path: `${output}/preview-${mobile ? 'mobile' : 'desktop'}-zh.png`, fullPage: true});
    await page.getByRole('button', {name: 'English', exact: true}).click();
    assert.equal(await page.locator('article:visible').count(), visibleCount);
    assert.deepEqual(await page.locator('article:visible').evaluateAll(cards => cards.map(c => c.dataset.locale)), Array(visibleCount).fill('en'));
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    await page.screenshot({path: `${output}/preview-${mobile ? 'mobile' : 'desktop'}-en.png`, fullPage: true});
    const links = await page.locator('a').evaluateAll(anchors => anchors.map(a => a.href));
    for (const link of links) {
      const response = await context.request.head(link);
      assert.equal(response.status(), 200, link);
    }
    results.push({viewport: mobile ? '390x844' : '1440x1080', metadata, realVideoPlayback: 'passed', pauseAndStaticFallback: 'passed', languageToggle: 'passed', noHorizontalOverflow: 'passed', reducedMotionDefault: mobile ? 'passed' : 'not_applicable', links: links.length});
    await context.close();
  }
  const page = await browser.newPage({viewport: {width: 1600, height: 600}});
  for (const id of ids) {
    const render = JSON.parse(await fs.readFile(path.join('out', id, 'render.json'), 'utf8'));
    const tiles = render.reviewFrames.map(frame => `<figure><img src="${base}out/${id}/frame-${frame}.png"><figcaption>frame ${frame} / ${(frame / 30).toFixed(2)}s</figcaption></figure>`).join('');
    await page.setContent(`<html><head><style>body{margin:0;padding:18px;background:#08101d;color:#ddd;font:16px sans-serif}h1{font-size:20px;margin:0 0 15px}section{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}figure{margin:0}img{width:100%;display:block}figcaption{padding:7px 0;color:#aab8ce}</style></head><body><h1>${id} — 8 sampled animation frames</h1><section>${tiles}</section></body></html>`);
    await page.waitForFunction(width => [...document.images].every(img => img.complete && img.naturalWidth === width), render.width);
    await page.screenshot({path: `${output}/contact-${id}.png`, fullPage: true});
  }
  assert.deepEqual(issues, []);
  await fs.writeFile(`${output}/browser-qa.json`, JSON.stringify({url, results, consoleAndPageErrors: issues, sampledFrameContactSheets: ids.length, nativeIPhonePlayback: 'not_tested'}, null, 2) + '\n');
  console.log(`PASS: desktop/mobile, ${ids.length} real video streams, motion toggle, reduced-motion fallback, bilingual switch and all download/source links.`);
} finally {
  await browser.close();
}
