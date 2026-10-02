import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {bundle} from '@remotion/bundler';
import {selectComposition, renderMedia, renderStill, openBrowser} from '@remotion/renderer';

// Adapted from LiveCanvas 8b6ca254b9536025945d0a1a4cf932ba4c905a0a (MIT).
const seriesName = process.argv.find(a => a.startsWith('--series='))?.split('=')[1] || 'classic';
const series = JSON.parse(await fs.readFile('series.json', 'utf8'))[seriesName];
if (!series) throw new Error(`Unknown series: ${seriesName}`);
const data = JSON.parse(await fs.readFile(series.data, 'utf8'));
if (data.demo !== false) throw new Error('Use source-verified project facts, not synthetic sample data.');
execFileSync(process.execPath, ['validate.mjs', `--series=${seriesName}`], {stdio: 'inherit'});
const ids = series.ids;
const selection = process.argv.find(a => a.startsWith('--only='))?.split('=')[1];
if (selection && !ids.includes(selection)) throw new Error(`Unknown composition: ${selection}`);
const stillsOnly = process.argv.includes('--stills');
const {coverFrame, reviewFrames} = series;
const outRoot = path.resolve('out');
const sourceSnapshot = await fs.readFile(series.entry);
const dataSnapshot = await fs.readFile(series.data);
const assets = JSON.parse(await fs.readFile(series.assets, 'utf8')).assets.filter(a => a.kind === 'generated-raster');
const sourceAssetHashes = {};
for (const asset of assets) sourceAssetHashes[asset.localPath] = createHash('sha256').update(await fs.readFile(asset.localPath)).digest('hex');
const serveUrl = await bundle({entryPoint: path.resolve(series.entry)});
const browserExecutable = process.env.LIVECANVAS_BROWSER || undefined;
const browser = await openBrowser('chrome', {browserExecutable});
const cli = path.resolve('node_modules/@remotion/cli/remotion-cli.js');
const runMediaTool = (tool, args) => execFileSync(process.execPath, [cli, tool, ...args], {encoding: 'utf8', maxBuffer: 8 * 1024 * 1024});
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
try {
  for (const id of ids.filter(id => !selection || selection === id)) {
    const out = path.join(outRoot, id);
    await fs.mkdir(out, {recursive: true});
    const composition = await selectComposition({serveUrl, id, browserExecutable, puppeteerInstance: browser});
    const duration = composition.durationInFrames / composition.fps;
    const common = {composition, serveUrl, browserExecutable, puppeteerInstance: browser};
    await renderStill({...common, frame: coverFrame, imageFormat: 'jpeg', jpegQuality: 97, output: path.join(out, 'cover.jpg')});
    await renderStill({...common, frame: coverFrame, imageFormat: 'png', output: path.join(out, 'cover.png')});
    for (const frame of reviewFrames) {
      await renderStill({...common, frame, imageFormat: 'png', output: path.join(out, `frame-${frame}.png`)});
    }
    let probe = null;
    if (!stillsOnly) {
      let lastLogged = -1;
      await renderMedia({...common, codec: 'h264', pixelFormat: 'yuv420p', colorSpace: 'bt709', imageFormat: 'png', crf: 14, outputLocation: path.join(out, 'motion.mp4'), concurrency: 2, onProgress: ({progress}) => {
        const quarter = Math.floor(progress * 4);
        if (quarter > lastLogged) {lastLogged = quarter; console.log(`${id}: ${Math.min(100, quarter * 25)}%`);}
      }});
      // The Remotion CLI supplies a matching local FFmpeg; no global installation.
      runMediaTool('ffmpeg', ['-v', 'error', '-y', '-i', path.join(out, 'motion.mp4'), '-filter_complex', '[0:v]scale=960:-2:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle', '-r', '15', '-t', String(duration), '-loop', '0', path.join(out, 'preview.gif')]);
      probe = JSON.parse(runMediaTool('ffprobe', ['-v', 'error', '-show_entries', 'format=duration:stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt,nb_frames', '-of', 'json', path.join(out, 'motion.mp4')]));
      const video = probe.streams.find(s => s.codec_type === 'video');
      if (!video || video.codec_name !== 'h264' || video.width !== composition.width || video.height !== composition.height || video.pix_fmt !== 'yuv420p' || video.r_frame_rate !== `${composition.fps}/1` || probe.streams.some(s => s.codec_type === 'audio') || Math.abs(Number(probe.format.duration) - duration) > .001) throw new Error(`${id}: video contract failed`);
      runMediaTool('ffmpeg', ['-v', 'error', '-y', '-i', path.join(out, 'motion.mp4'), '-ss', String(coverFrame/composition.fps), '-frames:v', '1', path.join(out, 'video-cover-frame.png')]);
    }
    const files = ['cover.jpg', 'cover.png', ...reviewFrames.map(f => `frame-${f}.png`), ...(!stillsOnly ? ['motion.mp4', 'preview.gif', 'video-cover-frame.png'] : [])];
    const fileHashes = {};
    for (const name of files) {
      const bytes = await fs.readFile(path.join(out, name));
      if (bytes.length === 0) throw new Error(`Empty render: ${id}/${name}`);
      fileHashes[name] = {bytes: bytes.length, sha256: sha256(bytes)};
    }
    if (sha256(await fs.readFile(series.entry)) !== sha256(sourceSnapshot) || sha256(await fs.readFile(series.data)) !== sha256(dataSnapshot)) throw new Error('Composition or facts changed during rendering; keep the candidate stable and rerun.');
    for (const [filename, hash] of Object.entries(sourceAssetHashes)) if (sha256(await fs.readFile(filename)) !== hash) throw new Error(`Asset changed during rendering: ${filename}`);
    const receipt = {id, series: seriesName, fps: composition.fps, durationInFrames: composition.durationInFrames, width: composition.width, height: composition.height, coverFrame, coverTime: coverFrame/composition.fps, reviewFrames, demo: data.demo, baseline: data.baseline, sourceSha256: sha256(sourceSnapshot), dataSha256: sha256(dataSnapshot), sourceAssetHashes, mode: stillsOnly ? 'stills' : 'full', probe, files: fileHashes};
    await fs.writeFile(path.join(out, 'render.json'), JSON.stringify(receipt, null, 2) + '\n');
    console.log(`Rendered ${id}: ${receipt.mode}, cover=${receipt.coverTime}s`);
  }
} finally {
  await browser.close({silent: true});
}
