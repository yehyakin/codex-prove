import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';

const seriesName = process.argv.find(a => a.startsWith('--series='))?.split('=')[1] || 'classic';
const series = JSON.parse(await fs.readFile('series.json', 'utf8'))[seriesName];
assert.ok(series, `Unknown series: ${seriesName}`);
const data = JSON.parse(await fs.readFile(series.data, 'utf8'));
const destination = path.resolve(series.exportDirectory);
await fs.mkdir(destination, {recursive: true});
const hashes = [];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const sourceHash = hash(await fs.readFile(series.entry));
for (const id of series.ids) {
  const out = path.resolve('out', id);
  const render = JSON.parse(await fs.readFile(path.join(out, 'render.json'), 'utf8'));
  assert.equal(render.mode, 'full');
  assert.equal(render.sourceSha256, sourceHash);
  if (render.dataSha256) assert.equal(render.dataSha256, hash(await fs.readFile(series.data)));
  for (const [filename, expected] of Object.entries(render.sourceAssetHashes || {})) assert.equal(hash(await fs.readFile(filename)), expected, `Asset changed: ${filename}`);
  for (const [from, extension] of [['cover.png', 'png'], ['preview.gif', 'gif']]) {
    const filename = `${id}.${extension}`;
    const bytes = await fs.readFile(path.join(out, from));
    assert.equal(hash(bytes), render.files[from].sha256);
    const target = path.join(destination, filename);
    try {
      const prior = await fs.readFile(target);
      assert.equal(hash(prior), hash(bytes), `Existing asset differs; preserve it before replacing ${filename}`);
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      await fs.copyFile(path.join(out, from), target, fs.constants.COPYFILE_EXCL);
    }
    assert.equal(hash(await fs.readFile(target)), hash(bytes));
    hashes.push({filename, bytes: bytes.length, sha256: hash(bytes)});
  }
}
await fs.writeFile(path.join(destination, 'manifest.json'), JSON.stringify({status: 'local-preview-not-integrated', asOf: data.asOf, factsBaseline: data.baseline, sourceSha256: sourceHash, artwork: series.description, assets: hashes}, null, 2) + '\n');
console.log(`Verified ${hashes.length} PNG/GIF assets exported to ${destination}; existing README/SVG not changed.`);
