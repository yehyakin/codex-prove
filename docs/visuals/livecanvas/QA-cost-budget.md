# Cost budget edition: verification

Verified 2026-10-01, local files and loopback preview only. User-confirmed comparison baseline: all GPT-6 Astra.

## Facts and arithmetic

- Official Standard Codex rates opened and read; numeric extract saved in evidence/cost-budget-rates.json.
- 1M uncached input + 0.1M billed output: all-Astra 375 credits, all-Sol 75, all-Luna 3.75.
- Assumed 80% Sol / 20% Luna in each token category: 60.75 credits, plus 3.75 hypothetical coordination credits = 64.5.
- 64.5 / 375 = 17.2%; illustrative saving = 82.8%. Not measured, not fixed quotas, not equal-quality or subscription/allowance evidence.
- Eight existing project claims checked against three committed snapshots. Both actual generated images reviewed for every numeric label and qualifier.

## Render and visual checks

- Both language variants: 1600×900, 30 fps, 180 frames / 6 seconds, H.264/yuv420p, no audio. Cover frame 156 = 5.2 seconds; exactly matches the last frame 179.
- Decoded-video/cover RMS: Chinese 3.031; English 3.087 (threshold <4).
- Both GIFs: 90 frames / 6000 ms.
- Main agent inspected both generated sources, full source/render comparisons, 16 sampled frames and four real-browser screenshots. No clipped labels, changed figures, missing glyphs or hidden disclaimer found.
- Pixel invariants cover header, headline, footer, all assumptions and both amount/percentage labels across frames 0, 18, 45, 70, 98, 126, 156, 179. Only comparison connectors change exposure.
- Source/render diagnostic normalization is not asserted pixel-identical: browser interpolation differs from the diagnostic resampler. Full-cover consistency and video-frame tolerance are separately checked above.

## Browser

- Dedicated Playwright CLI Chromium session against http://127.0.0.1:50008/preview.html; no user browser account accessed.
- Desktop viewport 1440×1100; narrow viewport 390×844. Six visible cards for each selected language, no horizontal overflow, visible images loaded.
- Chinese and English buttons switch the first card to the corresponding new budget edition. Both new MP4s play; observed clock progress and readyState=4. Other themes remain available.
- Static toggle pauses all videos and hides video layers while showing the loaded cover. Reduced-motion emulation also disables motion.
- All 65 unique same-origin gallery resources returned HTTP 200 with nonzero Content-Length; no console errors or warnings.
- Screenshots and snapshots are under output/playwright/cost-budget/. Compact receipt: qa-output/cost-budget/browser.json.

## Native resources

- Both JPEG/MOV identifiers matched, timed metadata points to 5.2 seconds, and PHLivePhoto local loads passed.
- Both .pvt packages and transport ZIPs were generated; package resource hashes verified. Photos was not opened and no photo-library import was requested.
- iPhone playback, third-party uploads, wallpaper support and photo-library import remain untested/not requested. A ZIP is a transport container, not an inline Live Photo.

## Scope and production notes

- New sibling cost-budget series; previous cost images, sources, renders and public exports retained.
- Only the two cost-gallery cards switched edition. Original six displayed themes retained; language variants do not add themes.
- No change to tracked runtime code, root README, existing SVGs, routing quotas or dependencies. No commit, push, merge, deployment or publication.
- Initial direct execution of the retained browser wrapper lacked execute permission; running it with bash worked without changing its permissions.
- Initial repository checks found the pending QA link before this file existed, then a wrong relative-link depth in the new export README. Both targets were corrected before the final verification run.
