import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';

const root = path.resolve('../../..');
const seriesName = process.argv.find(a => a.startsWith('--series='))?.split('=')[1] || 'classic';
const series = JSON.parse(await fs.readFile('series.json', 'utf8'))[seriesName];
assert.ok(series, `Unknown series: ${seriesName}`);
const data = JSON.parse(await fs.readFile(series.data, 'utf8'));
assert.equal(data.demo, false);
assert.equal(data.releaseStatus, 'candidate-not-released');
assert.match(data.baseline, /^[a-f0-9]{40}$/);
const expectedCounts = {classic: {claims: 6, models: 3}, polish: {claims: 10, models: 0}, cost: {claims: 8, models: 0}, 'cost-budget': {claims: 8, models: 0}}[seriesName];
assert.ok(expectedCounts, `No verified facts contract for ${seriesName}`);
assert.equal(data.claims.length, expectedCounts.claims);
assert.equal(data.models.length, expectedCounts.models);
const evidence = new Map();
// README integration changes layout and adds new, separately checked budget text.
// Keep the committed source snapshot immutable; check every cited excerpt in the
// working documentation too. Runtime profiles still require equality. The one
// reviewed routing update below pins complete entrypoint bytes, not arbitrary
// drift; its archived and current excerpts must both continue to match.
const editableDocs = new Set(['README.md', 'docs/costs.md']);
const reviewedRuntimeUpdates = new Map([
  // docs/research/2026-10-02-host-identity-routing.md; no rendered claim changed.
  ['.agents/skills/codex-prove/SKILL.md', '4540ebd658dfc154074d485a1ddf7bc4715ee7eb4b8184c00bf73326dca25f1d'],
]);
for (const source of data.sources) {
  assert.ok(source.url.includes(data.baseline));
  assert.ok(!evidence.has(source.id));
  const bytes = execFileSync('git', ['show', `${data.baseline}:${source.path}`], {cwd: root});
  const currentBytes = await fs.readFile(path.join(root, source.path));
  const text = bytes.toString('utf8');
  const currentText = currentBytes.toString('utf8');
  const currentSha256 = createHash('sha256').update(currentBytes).digest('hex');
  const reviewedUpdate = !editableDocs.has(source.path) && currentText !== text;
  if (reviewedUpdate) assert.equal(currentSha256, reviewedRuntimeUpdates.get(source.path), `Source drift: ${source.path}`);
  evidence.set(source.id, {
    source, text, sha256: createHash('sha256').update(bytes).digest('hex'),
    currentText, currentSha256,
    validation: editableDocs.has(source.path) ? 'archived-and-current-excerpts' : reviewedUpdate ? 'reviewed-working-snapshot-and-excerpts' : 'exact-snapshot',
  });
}
for (const claim of data.claims) {
  const entry = evidence.get(claim.sourceId);
  assert.ok(entry, `Unknown source: ${claim.sourceId}`);
  assert.ok(entry.text.includes(claim.excerpt), `Excerpt changed: ${claim.id}`);
  assert.ok(entry.currentText.includes(claim.excerpt), `Current excerpt changed: ${claim.id}`);
}
for (const model of data.models) {
  const text = evidence.get(model.sourceId).text;
  assert.equal(text.match(/^model = "([^"]+)"$/m)?.[1], model.model);
  assert.equal(text.match(/^model_reasoning_effort = "([^"]+)"$/m)?.[1], model.effort);
}
const composition = await fs.readFile(series.entry, 'utf8');
if (seriesName === 'cost-budget') {
  const budget = data.budget;
  const rateEvidence = JSON.parse(await fs.readFile(budget.evidencePath, 'utf8'));
  assert.equal(rateEvidence.source, 'https://learn.chatgpt.com/docs/pricing');
  assert.equal(rateEvidence.speed, 'Standard');
  assert.equal(rateEvidence.accessedAt, data.asOf);
  assert.equal(budget.cachedInputTokens, 0);
  assert.equal(budget.baselineModel, 'GPT-6 Astra');
  assert.deepEqual(budget.perModelTokenShares, {sol: .8, luna: .2, astra: 0});
  let routed = 0;
  for (const [model, rates] of Object.entries(rateEvidence.rates)) {
    const cost = budget.inputTokens / 1e6 * rates.input + budget.outputTokensIncludingBilledReasoning / 1e6 * rates.output;
    assert.equal(cost, budget.fullModelCosts[model]);
    routed += cost * budget.perModelTokenShares[model];
  }
  assert.equal(routed, budget.routedCredits);
  assert.equal(budget.extraCoordinationCredits, budget.fullModelCosts.sol * .05);
  assert.equal(routed + budget.extraCoordinationCredits, budget.totalCredits);
  assert.equal(budget.baselineCredits, budget.fullModelCosts.astra);
  assert.equal(Number((100 * budget.totalCredits / budget.baselineCredits).toFixed(8)), budget.costPercentOfBaseline);
  assert.equal(Number((100 * (1 - budget.totalCredits / budget.baselineCredits)).toFixed(8)), budget.savingsPercent);
  console.log(`PASS: illustrative budget ${budget.baselineCredits} -> ${budget.totalCredits} credits; ${budget.savingsPercent}% versus all-Astra, including ${budget.extraCoordinationCredits} extra credits; not measured.`);
}
assert.doesNotMatch(composition, /Math\.random|Date\.now|setInterval|animation\s*:/);
assert.match(composition, /useCurrentFrame/);
if (seriesName === 'classic') {
  assert.match(composition, /候选方案/);
  assert.match(composition, /仅按需/);
  assert.match(composition, /只读分析/);
  assert.match(composition, /同一上下文/);
} else {
  assert.match(composition, /staticFile/);
  const assets = JSON.parse(await fs.readFile(series.assets, 'utf8')).assets;
  assert.equal(assets.length, series.ids.length);
  for (const id of series.ids) {
    const asset = assets.find(a => a.id === id);
    assert.ok(asset, `Missing image: ${id}`);
    assert.equal(asset.kind, 'generated-raster');
    assert.equal(asset.factCheck, 'passed');
    assert.equal(asset.textReview, 'passed');
    assert.equal(asset.localPath, `public/media/${seriesName}/${id}.png`);
    assert.equal(createHash('sha256').update(await fs.readFile(asset.localPath)).digest('hex'), asset.sha256);
  }
}
await fs.mkdir('out', {recursive: true});
await fs.writeFile(`out/source-evidence${seriesName === 'classic' ? '' : '-'+seriesName}.json`, JSON.stringify({baseline: data.baseline, asOf: data.asOf, claims: data.claims, sources: [...evidence.values()]}, null, 2) + '\n');
console.log(`PASS: ${data.claims.length} claims, ${data.models.length} model/effort mappings, ${data.sources.length} committed source snapshots, deterministic animation source${seriesName === 'classic' ? '' : ', '+series.ids.length+' reviewed raster assets'}.`);
