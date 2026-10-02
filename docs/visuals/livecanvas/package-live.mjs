import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';

if (process.platform !== 'darwin') throw new Error('Live Photo pairing requires macOS; static/video previews remain available.');
const seriesName = process.argv.find(a => a.startsWith('--series='))?.split('=')[1] || 'classic';
const series = JSON.parse(await fs.readFile('series.json', 'utf8'))[seriesName];
if (!series) throw new Error(`Unknown series: ${seriesName}`);
const data = JSON.parse(await fs.readFile(series.data, 'utf8'));
const ids = series.ids;
for (const id of ids) {
  const out = path.resolve('out', id);
  const render = JSON.parse(await fs.readFile(path.join(out, 'render.json'), 'utf8'));
  if (render.mode !== 'full') throw new Error(`${id}: full video render required`);
  if (createHash('sha256').update(await fs.readFile(series.entry)).digest('hex') !== render.sourceSha256) throw new Error(`${id}: source changed after render`);
  for (const [filename, hash] of Object.entries(render.sourceAssetHashes || {})) if (createHash('sha256').update(await fs.readFile(filename)).digest('hex') !== hash) throw new Error(`${id}: asset changed after render: ${filename}`);
  const name = `codex-prove-${id}.pvt`;
  const pair = path.join(out, 'live');
  const stdout = execFileSync(path.resolve('.build/pair-live-photo'), [path.join(out, 'cover.jpg'), path.join(out, 'motion.mp4'), pair, String(render.coverTime), String(render.fps)], {encoding: 'utf8', timeout: 65000});
  const manifest = JSON.parse(stdout);
  if (!manifest.metadataVerified || manifest.localPHLivePhotoLoad !== 'passed') throw new Error(`${id}: native validation failed`);
  const packageReceipt = JSON.parse(execFileSync(process.env.LIVECANVAS_PYTHON || 'python3', ['tools/package_live_photo.py', pair, path.join(out, name)], {encoding: 'utf8', timeout: 30000}));
  packageReceipt.photosImport = 'not_requested';
  await fs.writeFile(path.join(out, 'package-receipt.json'), JSON.stringify(packageReceipt, null, 2) + '\n');
  execFileSync('/usr/bin/ditto', ['-c', '-k', '--keepParent', path.join(out, name), path.join(out, `${name}.zip`)], {timeout: 30000});
  const delivery = {
    mode: 'file', id, asOf: data.asOf, baseline: render.baseline,
    preview: {cover: 'cover.jpg', losslessCover: 'cover.png', video: 'motion.mp4', animation: 'preview.gif'},
    livePhotoPackage: name, transportZip: `${name}.zip`,
    identifier: manifest.identifier, metadataVerified: manifest.metadataVerified,
    stillImageTime: manifest.readbackStillTime, localPHLivePhotoLoad: manifest.localPHLivePhotoLoad,
    resourceHashes: packageReceipt.sha256,
    zipSha256: createHash('sha256').update(await fs.readFile(path.join(out, `${name}.zip`))).digest('hex'),
    photosImport: 'not_requested', iPhonePlayback: 'not_tested', wallpaper: 'not_tested', socialUpload: 'not_tested',
    compatibility: 'A .pvt resource package, not a promise that iPhone Files or a chat client can preview or import it.',
    editableProject: '../..'
  };
  for (const filename of [series.data, series.assets, series.sources]) await fs.copyFile(filename, path.join(out, filename));
  await fs.writeFile(path.join(out, 'delivery.json'), JSON.stringify(delivery, null, 2) + '\n');
  console.log(`${id}: paired metadata, ${render.coverTime}s still time, PHLivePhoto local load and package hashes passed; Photos not opened.`);
}
