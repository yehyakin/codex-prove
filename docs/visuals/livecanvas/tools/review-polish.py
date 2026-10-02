#!/usr/bin/env python3
"""Create diagnostic comparisons only; never change any artwork or render."""
import json
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageOps, ImageStat

root = Path(__file__).resolve().parents[1]
series_name = next((arg.split('=', 1)[1] for arg in sys.argv[1:] if arg.startswith('--series=')), 'polish')
assert series_name in ('polish', 'cost', 'cost-budget'), series_name
output = root / 'qa-output' / series_name
output.mkdir(parents=True, exist_ok=True)
series = json.loads((root / 'series.json').read_text(encoding='utf-8'))[series_name]
results = []


def pair(top, bottom, target, labels=('SOURCE / normalized', 'RENDER / final hold')):
    board = Image.new('RGB', (top.width, top.height + bottom.height + 48), '#111827')
    draw = ImageDraw.Draw(board)
    draw.text((12, 5), labels[0], fill='#ffffff')
    board.paste(top, (0, 24))
    draw.text((12, top.height + 29), labels[1], fill='#ffffff')
    board.paste(bottom, (0, top.height + 48))
    board.save(target)


for variant in series['ids']:
    folder = root / 'out' / variant
    receipt = json.loads((folder / 'render.json').read_text(encoding='utf-8'))
    size = (receipt['width'], receipt['height'])
    cover = Image.open(folder / 'cover.png').convert('RGB')
    raw = Image.open(root / 'public' / 'media' / series_name / f'{variant}.png').convert('RGB')
    contained = ImageOps.contain(raw, size, Image.Resampling.LANCZOS)
    source = Image.new('RGB', size, '#0B111E')
    source.paste(contained, ((size[0] - contained.width)//2, (size[1] - contained.height)//2))
    pair(source, cover, output / f'comparison-{variant}.png')
    pair(source.crop((0, 620, 1600, 900)), cover.crop((0, 620, 1600, 900)), output / f'detail-{variant}.png')
    frames = receipt['reviewFrames']
    board = Image.new('RGB', (1600, 504), '#111827')
    draw = ImageDraw.Draw(board)
    invariants = []
    title_edge = 660 if series_name in ('cost', 'cost-budget') else 632 if variant.startswith('ownership') else 620 if variant.startswith('evidence') else 484
    for index, frame in enumerate(frames):
        pixels = Image.open(folder / f'frame-{frame}.png').convert('RGB')
        tile = pixels.resize((400, 225), Image.Resampling.LANCZOS)
        x, y = (index % 4) * 400, (index // 4) * 252
        board.paste(tile, (x, y))
        draw.text((x+8, y+231), f'{variant} / frame {frame} / {frame/receipt["fps"]:.2f}s', fill='#ffffff')
        for name, crop in [('header', (0, 0, 1600, 120)), ('title', (0, 130, title_edge, 590)), ('footer', (0, 810, 1600, 900))]:
            assert ImageChops.difference(pixels.crop(crop), cover.crop(crop)).getbbox() is None, (variant, frame, name)
        if variant.startswith('evidence'):
            assert ImageChops.difference(pixels.crop((0, 670, 1600, 805)), cover.crop((0, 670, 1600, 805))).getbbox() is None, (variant, frame, 'verdict alternatives must stay stable')
        if series_name == 'cost':
            assert ImageChops.difference(pixels.crop((0, 715, 1600, 805)), cover.crop((0, 715, 1600, 805))).getbbox() is None, (variant, frame, 'cost accounting note must stay stable')
            assert ImageChops.difference(pixels.crop((0, 420, 700, 585)), cover.crop((0, 420, 700, 585))).getbbox() is None, (variant, frame, 'supporting text must stay stable')
            assert ImageChops.difference(pixels.crop((850, 468, 1118, 507)), cover.crop((850, 468, 1118, 507))).getbbox() is None, (variant, frame, 'optional qualifier must stay stable')
        if series_name == 'cost-budget':
            assert ImageChops.difference(pixels.crop((0, 665, 1600, 805)), cover.crop((0, 665, 1600, 805))).getbbox() is None, (variant, frame, 'budget assumptions must stay stable')
            assert ImageChops.difference(pixels.crop((1100, 180, 1580, 660)), cover.crop((1100, 180, 1580, 660))).getbbox() is None, (variant, frame, 'credit amounts and baseline labels must stay stable')
        invariants.append(frame)
    board.save(output / f'contact-{variant}.png')
    results.append({'id': variant, 'sourcePixels': list(raw.size), 'renderPixels': list(size), 'normalization': 'contain, LANCZOS diagnostic normalization only', 'sourceVsRenderRms': ImageStat.Stat(ImageChops.difference(source, cover)).rms, 'stableHeaderTitleFooterFrames': invariants, 'comparison': f'qa-output/{series_name}/comparison-{variant}.png', 'focusedComparison': f'qa-output/{series_name}/detail-{variant}.png', 'contactSheet': f'qa-output/{series_name}/contact-{variant}.png', 'visualReview': 'pending'})
    print(f'{variant}: actual reference/render comparison, 8 frame contact sheet, stable title/header/footer PASS')
(output / 'comparison-receipt.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
