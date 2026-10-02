# Selected-series design QA

Date: 2026-10-01. Scope: six rendered illustration variants, not a new app or website.

final result: passed

## Findings

No actionable P0/P1/P2 visual mismatch remains in the final rendered illustrations.
The first opening frames had a P2 masking artifact; the revision and evidence are recorded below.

## Comparison targets and state

- Source visual truth: `public/media/polish/{routing,ownership,evidence}-{zh,en}.png`.
  The Chinese routing master is the user's selected first concept. Other posters follow that direction.
- Implementation: `out/<variant>/cover.png`, actual Remotion/Chromium rendering of `src/polish.tsx`.
- Source pixels: 1672 × 941. Composition viewport and output: 1600 × 900, scale 1.
  The image is contained in the frame, not cropped or stretched. There is no device frame or browser chrome.
- Density normalization: the diagnostic comparison contains the source at 1600 × 900 using Pillow LANCZOS
  above the actual Chromium cover. Minor resampling differences are expected; typography is not re-created.
- Matched state: dark theme, full illustration visible, frame 156 / 5.2 seconds.
  Eight actual frames per variant also cover entry, progression and final hold:
  0, 18, 45, 70, 98, 126, 156 and 179. All 48 sampled frames were visually reviewed.

| Variant | Full-view paired input | Focused paired input | Motion states |
| --- | --- | --- | --- |
| routing-zh | `qa-output/polish/comparison-routing-zh.png` | `qa-output/polish/detail-routing-zh.png` | `qa-output/polish/contact-routing-zh.png` |
| routing-en | `qa-output/polish/comparison-routing-en.png` | `qa-output/polish/detail-routing-en.png` | `qa-output/polish/contact-routing-en.png` |
| ownership-zh | `qa-output/polish/comparison-ownership-zh.png` | `qa-output/polish/detail-ownership-zh.png` | `qa-output/polish/contact-ownership-zh.png` |
| ownership-en | `qa-output/polish/comparison-ownership-en.png` | `qa-output/polish/detail-ownership-en.png` | `qa-output/polish/contact-ownership-en.png` |
| evidence-zh | `qa-output/polish/comparison-evidence-zh.png` | `qa-output/polish/detail-evidence-zh.png` | `qa-output/polish/contact-evidence-zh.png` |
| evidence-en | `qa-output/polish/comparison-evidence-en.png` | `qa-output/polish/detail-evidence-en.png` | `qa-output/polish/contact-evidence-en.png` |

The focused comparisons cover the lower labels, handoff and result legend at readable size.
Their diagnostic crop starts at y=620; a label touching that crop boundary is not clipping in the full artwork.

## Five required fidelity surfaces

1. Fonts/typography: headline, small labels, Chinese glyphs and English wrapping stay in the source pixels.
   No fallback-font substitution, new wrapping or truncated text was found in the full and focused comparisons.
   The title, top identity and footer remain pixel-stable across the eight sampled frames.
2. Spacing/layout rhythm: all artwork retains the original alignment, hierarchy, margins and proportions.
   Both ownership lanes illuminate together; only the handoff proceeds sequentially.
3. Colors/tokens: navy, ivory, orange, mint and violet stay in the original assets.
   The intentional dimming is temporary and feathered; the final hold has no mask.
   State labels carry words and distinct symbols, not color alone.
4. Image quality/assets: no source illustration or icon was replaced by CSS drawings, SVG or placeholder art.
   The video uses lossless PNG intermediate frames, H.264/yuv420p BT.709 output and proportional containment.
   Masks control exposure over the actual image. They do not reconstruct the artwork.
5. Copy/content: poster labels were checked against the ten source-backed claims in `data-polish.json`.
   Routing alternatives are not a mandatory pipeline; ownership is not file locking or isolation;
   PASS/FIX/BLOCKED are alternative verdicts, not a claimed real run. No speed/cost measurements are implied.

## Comparison history

### Attempt 1 — blocked

- [P2] Visible rectangular dimming boundary in opening frames, especially around the routing branches.
  Location: `Reveal` in `src/polish.tsx`.
  Evidence: `qa-output/polish-attempt-1/contact-<variant>.png` and retained stills under `out/polish-attempt-1/`.
  Impact: the rectangular patch looked pasted over the selected fine-line illustration.
  Fix: replace rectangular feathering with a soft elliptical exposure mask and reduce initial opacity.

### Attempt 2 — passed

- Fresh stills and all six complete videos were rendered after the mask change.
- Post-fix evidence: the six current paired comparisons and contact sheets in the table above.
- The hard edge is absent; title, footer, source art and layout are unchanged.
- Exact final cover equality and 6-second GIF/video checks passed. No further visual fixes were made.

## Open questions and residual gaps

- The gallery now contains the new files, but its browser interactions have not been re-tested in this turn.
  Approval for a Playwright-only browser fallback was requested and has not been received.
  The original four-variant gallery's older browser results are not acceptance evidence for the updated gallery.
- These are fixed-layout illustrations, not responsive text layouts. Use the source PNG at a readable size;
  the preview includes text descriptions and direct downloads. Narrow-screen gallery UI remains unverified.
- Local PHLivePhoto loading is verified separately. iPhone playback, Photos import, lock screen and social upload are not tested.

## Implementation checklist

- [x] Preserve the selected original and all six generated sources with prompts and hashes.
- [x] Compare actual source/render pairs, including detailed text regions and all sampled motion states.
- [x] Resolve the P2 exposure-mask artifact, re-render and re-compare.
- [x] Verify output hashes, stable cover frame, video/GIF duration and local Live Photo metadata.
- [ ] Browser interaction QA of the updated gallery, only if the fallback is approved.

## Follow-up polish

No additional visual change is needed for the requested illustration handoff.
