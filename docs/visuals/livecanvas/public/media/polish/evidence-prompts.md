# Evidence poster asset provenance

- Tool: built-in ImageGen; no CLI fallback.
- Output canvas: 1672 × 941 pixels, opaque PNG.
- Chinese asset: `docs/visuals/livecanvas/public/media/polish/evidence-zh.png`.
- English asset: `docs/visuals/livecanvas/public/media/polish/evidence-en.png`.
- Input mechanism for every call: actual `referenced_image_paths`; `transparent_background: false`.
- References below use project-relative paths or generated-image basenames for portability. Prose prompts are verbatim.
- Three Chinese calls are one generation followed by two targeted corrections, yielding one final Chinese asset. The accepted Chinese asset is the sole English localization reference.

## Chinese 1 — companion poster generation

Reference: `exec-945fef37-0d2c-4604-bc06-58f1df60ff91.png (selected Routing Atlas reference)`.

Generated image: `exec-c745ac0c-f001-459d-8779-190919cf6c8a.png`.

```text
Use case: infographic-diagram.
Asset type: one finished Chinese evidence-verification poster for the existing CODEX PROVE LiveCanvas.
Input images: Image 1 is the selected Routing Atlas visual STYLE AND DESIGN-SYSTEM reference. Use the actual attached image; preserve its wide format, precise editorial typographic hierarchy, deep navy backdrop, premium softly lit metallic paths, fine line art, generous spacing, header rule and footer rule. This is a NEW companion poster about evidence checking, not a reproduction of its routing content. Generate ONE single poster, not options or a contact sheet.

Canvas: landscape 16:9, ideally 1672 × 941 pixels like the reference (1600 × 900 is also acceptable). Entire poster visible without cropping. No transparency.
Color palette: deep navy #0B111E background; ivory #F3F3EB headline and wordmark; orange #FF9364, mint #8DDBBF, violet #B4AAFF accents; quiet cool-gray secondary text. Clean 2D editorial technical graphic with delicately luminous metallic diagram paths and schematic document line art, matching Image 1 closely. Controlled soft lighting, not excessive bloom.
Header: match reference margins and hierarchy, at top-left the same small orange outlined P monogram and exact wordmark "CODEX PROVE"; exact top-right text "候选方案"; fine horizontal divider at about y=13% with a short orange segment at left.
Main composition: left 34% is a bold ivory two-line Chinese headline, with exact line breaks:
"交付之前"
"先核对证据"
Below it, the quiet-gray exact subtitle "检查真实结果，不只看完成汇报".
The right-side diagram must fit completely inside x=38%–95% and y=20%–70%. Draw three clear schematic document objects as three distinct inputs, arranged vertically on the left side of that diagram. Each has a crisp folded-corner outline and a few neutral short document lines; they are not physical paper. Their exact readable labels are "实际文件", "修改差异", and "测试与需求覆盖". Use three fine precise softly lit metallic curved paths, each originating at one distinct document input and visibly converging toward one right-side circular inspection-result node labeled exactly "检查结果". Direction of relationship is three actual evidence inputs into one inspection result. This is schematic evidence gathering, not a claim of any actual test run. No fabricated metrics, terminal logs, benchmark numbers, or fake test outputs.
Bottom verdict band: at y=77%–87%, present THREE INDEPENDENT outcome groups across the width, aligned with one another and equal in visual importance. They are alternatives, NOT successive steps. No arrows or paths between these groups. No numeric sequence. Use mint for PASS, orange for FIX, violet for BLOCKED, with plenty of separation and clear typography.
Exact text in group 1:
"PASS"
"证据齐全，覆盖要求"
Exact text in group 2:
"FIX"
"授权范围内继续修复"
Exact text in group 3:
"BLOCKED"
"没有安全的下一步"
Use small restrained line-art symbols if needed, consistent with Image 1, without adding written labels.
Footer: matching reference thin horizontal divider around y=90%, then exact quiet-gray footer text at lower left "候选工作流示意 · 不代表某次运行结果".

All quoted text must be rendered VERBATIM, correctly spelled, fully legible, once in the specified location. Use professional clean Chinese sans-serif typography with reference-like bold headline weight. No additional copy, no option numbers, no dates, no extra slogans, no watermark. Do not reuse the reference poster's old Direct/Solo/Assist/Coordinated labels or its old headline/footer. Do not imply PASS→FIX→BLOCKED sequence or a mandatory hierarchy. No performance guarantee, no success guarantee, no OS-security claim. Avoid photorealistic paper, desk, trays, wood, stamps, fake logs, decorative 3D props, photo mockups, or a second panel.
```

## Chinese 2 — punctuation and layout correction

Reference: `exec-c745ac0c-f001-459d-8779-190919cf6c8a.png`.

Generated image: `exec-74d05ec5-7977-4ff5-9fd1-0c93905f26db.png`.

```text
Use case: precise-object-edit with exact text correction.
Input image: Image 1 is the newly generated CODEX PROVE Chinese evidence poster and is the EDIT TARGET.
Make only these small production corrections to the provided poster; preserve every other pixel-level design choice as closely as possible, including exact colors, typography, line-art style, header/footer layout, icon shapes, hierarchy, and metallic softly lit three-input convergence paths. Keep the same 1672 × 941 landscape canvas.

1. The left subtitle currently has an unwanted terminal Chinese full stop. Replace the subtitle with EXACTLY "检查真实结果，不只看完成汇报" with NO final period, NO other punctuation added, and NO extra characters. Keep it a single line. Preserve its position, color and font, but reduce its size just slightly if needed so its right edge stays within x=36%.
2. Keep the right-hand diagram identical, but shift the entire diagram group vertically downward by 22 pixels so all three document objects, their labels, paths, dashed construction lines and result node fit within x=38%–95%, y=20%–70%. Do not change their horizontal positions or relationships. Exact labels stay "实际文件", "修改差异", "测试与需求覆盖", "检查结果".
3. Keep the three bottom verdict groups identical and independent, but shift the entire verdict band (all three groups including icons, text and short separators) DOWN by 45 pixels, putting it at about y=77%–87%. Keep enough clearance above the existing footer divider. Do not connect the groups with arrows or lines and do not imply sequence.

ALL other text must remain precisely unchanged:
Header wordmark "CODEX PROVE"; upper right "候选方案".
Headline line 1 "交付之前"; headline line 2 "先核对证据".
Bottom independent group 1 "PASS" / "证据齐全，覆盖要求".
Bottom independent group 2 "FIX" / "授权范围内继续修复".
Bottom independent group 3 "BLOCKED" / "没有安全的下一步".
Footer "候选工作流示意 · 不代表某次运行结果".

Do not change the headline, header or footer. No other visual redesign. No additional text, no watermark, no log data, no performance claims. This remains one candidate-workflow schematic, not actual run results. Generate ONE corrected poster.
```

## Chinese 3 — final lower-band alignment

Reference: `exec-74d05ec5-7977-4ff5-9fd1-0c93905f26db.png`.

Generated image: `exec-c0f4c7bc-7ad7-494c-aa38-4d711570fbc7.png`.

```text
Use case: precise-object-edit.
Image 1 is the exact edit target. Make ONE tiny layout adjustment only: move the ENTIRE lower verdict band DOWN by exactly 24 pixels on this 1672 × 941 canvas. The top of the three circular icons should be around pixel y=725, and their bottom around y=816. Move the PASS / FIX / BLOCKED headings, the Chinese descriptions, and all short vertical separators by the same 24 pixels. Keep enough gap above the fixed footer divider at y=831. The three groups remain three independent alternative verdicts, with no connecting lines and no arrows.

Preserve EVERYTHING ELSE unchanged: the full diagram, all paths, all labels, headline, subtitle with no final period, header, footer, background, exact colors, typography, sizes, all text spellings, and canvas dimensions. Do not recreate or redesign the image; this is only the tiny lower-band vertical relocation.
Keep exact visible text:
CODEX PROVE
候选方案
交付之前
先核对证据
检查真实结果，不只看完成汇报
实际文件
修改差异
测试与需求覆盖
检查结果
PASS
证据齐全，覆盖要求
FIX
授权范围内继续修复
BLOCKED
没有安全的下一步
候选工作流示意 · 不代表某次运行结果
No new text or punctuation, no watermark. Generate one corrected image.
```

## English — localization of accepted Chinese poster

Reference: `docs/visuals/livecanvas/public/media/polish/evidence-zh.png`.

Generated image: `exec-ce8dcbb8-ccd9-4942-bcc7-7ef653b12924.png`.

```text
Use case: text-localization.
Asset type: English localization of the accepted CODEX PROVE evidence-verification poster.
Input images: Image 1 is the ACTUAL accepted Chinese evidence poster and is the EDIT TARGET, not merely a style reference.
Primary request: translate only the visible Chinese text into the exact English below. Produce ONE localized poster. Preserve all existing art and layout geometry as closely as possible.

Keep unchanged: 1672 × 941 landscape canvas; deep navy #0B111E backdrop and texture; ivory #F3F3EB typography; orange #FF9364, mint #8DDBBF and violet #B4AAFF accents; orange P monogram; exact "CODEX PROVE" wordmark; fine header and footer rules; all three schematic document icons; their positions; the softly lit metallic fine-line converging paths; the circular review-result icon; dashed construction lines; all PASS/FIX/BLOCKED symbols; short separators; three independent lower verdict groups. The three verdicts are ALTERNATIVES, not sequential stages. Do not add arrows or paths between them.
Only text size and line wrapping may change inside the EXISTING text slots to make English fit naturally. Do not move or resize the diagram, icons, paths, footer, or panels. Do not add new visual elements. Keep the same professional sans-serif typography and editorial hierarchy.

Replace text VERBATIM as follows:
- Top right "候选方案" becomes "CANDIDATE".
- Large left headline becomes EXACTLY TWO lines, using a smaller bold size to fit its existing left-column box:
  "Verify evidence"
  "before delivery"
- Left supporting sentence becomes "Inspect real results, not just reports." Keep it within the existing left-column supporting-text slot; two lines are allowed only if necessary.
- Document label "实际文件" becomes "Actual files".
- Document label "修改差异" becomes "Changes and diff".
- Document label "测试与需求覆盖" becomes "Tests and requirements". Keep this entire label in its existing position under the lower document, using a smaller font if needed.
- Right result label "检查结果" becomes "Review result".
- Keep heading "PASS" unchanged; replace its description with "Evidence covers the requirements". This longer description may use two lines within the existing PASS description slot, e.g. "Evidence covers" / "the requirements".
- Keep heading "FIX" unchanged; replace its description with "Continue authorized repairs". This may use two lines within the existing FIX description slot, e.g. "Continue authorized" / "repairs".
- Keep heading "BLOCKED" unchanged; replace its description with "No safe next step".
- Footer becomes "Candidate workflow illustration · not a real run result".

All quoted English must be correctly spelled and completely legible. Do not add or remove words; preserve capitalization and punctuation exactly. No Chinese should remain. Keep "CODEX PROVE", "PASS", "FIX", and "BLOCKED" unchanged. Use only the listed visible English text and the existing P monogram, with no extra text, metrics, logs, dates, option numbers, slogans, or watermark. No claim of an actual completed run. Preserve the accepted image's artwork; this is localization, not redesign.
```
