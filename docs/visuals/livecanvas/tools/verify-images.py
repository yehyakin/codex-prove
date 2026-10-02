#!/usr/bin/env python3
"""Read-only pixel/duration checks of render artifacts; writes only a QA receipt."""
import hashlib
import json
import math
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

root = Path(__file__).resolve().parents[1]
series_name = next((arg.split('=', 1)[1] for arg in sys.argv[1:] if arg.startswith('--series=')), 'classic')
series = json.loads((root / 'series.json').read_text(encoding='utf-8'))[series_name]
for variant in series['ids']:
    folder = root / 'out' / variant
    render = json.loads((folder / 'render.json').read_text(encoding='utf-8'))
    assert render['mode'] == 'full'
    for filename, record in render['files'].items():
        content = (folder / filename).read_bytes()
        assert len(content) == record['bytes'], filename
        assert hashlib.sha256(content).hexdigest() == record['sha256'], filename
    cover_frame = render['coverFrame']
    last_frame = render['durationInFrames'] - 1
    duration = render['durationInFrames'] / render['fps']
    assert (folder / 'cover.png').read_bytes() == (folder / f'frame-{cover_frame}.png').read_bytes()
    assert (folder / f'frame-{cover_frame}.png').read_bytes() == (folder / f'frame-{last_frame}.png').read_bytes()
    assert (folder / 'frame-0.png').read_bytes() != (folder / 'cover.png').read_bytes()
    cover = Image.open(folder / 'cover.png').convert('RGB')
    decoded = Image.open(folder / 'video-cover-frame.png').convert('RGB')
    assert cover.size == decoded.size == (render['width'], render['height'])
    rms = ImageStat.Stat(ImageChops.difference(cover, decoded)).rms
    combined_rms = math.sqrt(sum(channel * channel for channel in rms) / 3)
    psnr = 20 * math.log10(255 / combined_rms) if combined_rms else None
    assert combined_rms < 4, ('cover/video frame mismatch', combined_rms)
    gif = Image.open(folder / 'preview.gif')
    gif_frames = gif.n_frames
    duration_ms = 0
    for frame in range(gif_frames):
        gif.seek(frame)
        duration_ms += gif.info.get('duration', 0)
    assert gif_frames > 2
    assert abs(duration_ms - duration * 1000) <= 200, duration_ms
    result = {
        'renderHashes': 'passed', 'dimensions': [render['width'], render['height']],
        'sameCompositionCoverFrame': cover_frame, 'coverTime': render['coverTime'],
        'coverMatchesSpecifiedFrame': True, 'stableThroughFinalFrame': True,
        'decodedVideoFrameRms': combined_rms, 'decodedVideoFramePsnrDb': psnr,
        'gifFrames': gif_frames, 'gifDurationMs': duration_ms,
        'visualReview': 'pending', 'fontAndClippingReview': 'pending',
        'note': 'Pixel similarity checks do not replace visual inspection or validate iPhone playback.'
    }
    (folder / 'image-qa.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'{variant}: hashes, exact stable cover, decoded frame RMS={combined_rms:.3f}, GIF {gif_frames} frames/{duration_ms}ms PASS')
