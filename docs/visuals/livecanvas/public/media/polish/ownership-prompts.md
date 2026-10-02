# Ownership illustration provenance

Both images were produced with the built-in ImageGen tool. No CLI fallback was used. The original generated files remain in place; project PNGs are byte-identical copies. Both project images are 1672 × 941 pixels.

## Chinese asset

- Project path: `docs/visuals/livecanvas/public/media/polish/ownership-zh.png`
- Original generated-image basename: `exec-9f9c3867-15b5-4fdc-8fb5-852b01ce9c62.png`
- Reference generated-image basename: `exec-945fef37-0d2c-4604-bc06-58f1df60ff91.png`
- Reference role: user-selected style and layout reference.
- `transparent_background`: `false`
- QA: All requested Chinese labels are present and readable; two independent scopes each connect to exactly one owner with no crossing or shared connection. The handoff stops the old owner and writing processes, preserves and inspects changes, then assigns the new owner before writes resume. The footer explicitly distinguishes a workflow agreement from file locks or isolation.

### Exact submitted prompt

```text
Use case: infographic-diagram
Asset type: a finished Chinese ownership explainer illustration for the existing CODEX PROVE LiveCanvas, landscape 1672 x 941 (same ratio as the reference), designed to be contained at 1600 x 900.
Input images: Image 1 is the user's selected STYLE AND LAYOUT REFERENCE, not text to reproduce. Use the actual supplied reference image to match its precise dark graphic routing-atlas language.
Primary request: Create ONE final illustration teaching one active owner per write scope, with independent scopes able to proceed in parallel. Show a correct three-step handoff below.

Style: Match Image 1's midnight navy background, ivory large bold Chinese typography, fine softly lit metallic routing lines, sparse technical guide marks, tiny outlined file/owner icons, restrained orange/mint/violet accents, precise flat graphic feel. Palette: midnight #0B111E, ivory #F3F3EB, orange #FF9364, mint #8DDBBF, violet #B4AAFF. Keep the same quiet header and footer framing, thin full-width rules and generous negative space. No large cards.
Header: Preserve the reference-style small outlined P monogram and CODEX PROVE wordmark at top left, and the exact Chinese text "候选方案" at top right. Header rule at roughly y13%.
Composition: Left 32% is typography, starting x4.7%, y28%. Main headline in two large readable lines: "同一写入范围" then "只设一个负责人". Supporting line below in muted ivory: "独立范围可并行". Do not clip or overlap any text.
Right diagram: Fit entirely within x35%-95%, y23%-69%. Two clearly separate, independent, noncrossing horizontal routing lanes. Upper lane: a small outlined file-scope symbol labelled "范围 A" connected by one softly lit orange metallic line to exactly one simple outlined single-person owner symbol labelled "负责人 A". Lower lane: a separate small outlined file-scope symbol labelled "范围 B" connected by one softly lit mint metallic line to exactly one simple outlined single-person owner symbol labelled "负责人 B". Make each pair and its one-to-one relationship unmistakable, with clean spacing and small route nodes. No connection between the two scopes, no shared owner, no third owner.
Handoff: Across the width beneath the main content at y78%-87%, a secondary left-to-right three-step line. Optional small heading "交接时". Render these exact three labels, in this order, connected by clear rightward arrows:
"停止原负责人及写入进程" → "保留并检查改动" → "指定新负责人后再写入"
All three labels must be highly legible, neither shortened nor paraphrased. Subtle small nodes with orange, ivory, and mint emphasis; no numbered option markers.
Footer: Under the bottom framing rule, one exact footnote in legible muted ivory: "工作流约定，不是文件锁或隔离机制".

Text accuracy: All quoted Chinese text must be rendered verbatim, crisply typeset in a modern bold/regular Chinese sans serif as appropriate. The only visible words are the specified wordmark, heading/support, scope/owner labels, handoff labels, optional "交接时", and footnote. No unrelated text.
Semantic constraints: Ownership is a workflow agreement, NOT an operating-system lock or isolation. Do not draw file padlocks, shields, walls, jail boxes, OS-enforcement badges, or blocked files. During handoff, the old owner AND mutating processes stop, changes are preserved and inspected, then the new owner is assigned BEFORE further writes. The A/B lanes are examples of independent scopes, not a claim that a fixed number of agents or model assignments is required.
Avoid: physical desks, paper trays, 3D still-life scenes, books, plants, photoreal objects, chunky cards, fake data, metrics, extra slogans, watermarks, option numbers, clutter, cropped text.
```

## English asset

- Project path: `docs/visuals/livecanvas/public/media/polish/ownership-en.png`
- Original generated-image basename: `exec-b1efd2d0-c254-4d9f-9aad-626e290dbfd4.png`
- Reference asset (project-relative): `docs/visuals/livecanvas/public/media/polish/ownership-zh.png`
- Reference role: approved Chinese edit target; text localization only.
- `transparent_background`: `false`
- QA: Every specified English replacement is present and readable. All three handoff labels remain distinct, with arrows between them and no text overlap. The artwork, pairwise scope/owner relationships, palette, framing and overall geometry are visually preserved. The Chinese project PNG was verified unchanged by comparison with its original generated file.

### Exact submitted prompt

```text
Use case: text-localization
Asset type: English localized version of the supplied finished CODEX PROVE ownership infographic.
Input images: Image 1 is the approved Chinese EDIT TARGET. Preserve this specific artwork; do not redesign it.
Primary request: Translate ONLY the Chinese text into the exact English replacements below. Produce ONE finished English image with the same 1672 x 941 landscape dimensions and ratio.

Exact text replacements:
- Top-right "候选方案" becomes "CANDIDATE".
- The two-line main headline becomes:
"One write scope."
"One active owner."
- The supporting line becomes two lines:
"Independent scopes"
"can run in parallel."
- "范围 A" becomes "Scope A".
- "范围 B" becomes "Scope B".
- "负责人 A" becomes "Owner A".
- "负责人 B" becomes "Owner B".
- "交接时" becomes "HANDOFF".
- The first handoff step becomes two lines:
"Stop the old owner"
"and its writing processes"
- The second handoff step becomes two lines:
"Preserve and"
"inspect changes"
- The third handoff step becomes two lines:
"Assign the new owner,"
"then resume writes"
- The footer becomes exactly:
"Workflow agreement, not a file lock or isolation."

Invariants: Keep the CODEX PROVE wordmark and outlined P monogram unchanged. Preserve the background, midnight/ivory/orange/mint/violet palette, header/footer rules, precise softly lit metallic lines, guide circles, file icons, owner icons, all nodes, routes, spacing, geometry and noncrossing two-lane one-to-one relationships. Keep all non-text pixels and visual positions as close as possible to the original. No new art.
Typography: Adjust font size and line breaks ONLY within the existing text-label regions to fit English. Use the reference's bold/regular sans-serif hierarchy and corresponding colors. Keep the three handoff steps distinct and fully readable, with arrows clearly BETWEEN steps, never touching or running underneath text. Keep generous padding from the diagram and image edges; do not clip letters.
Accuracy: Render every English phrase verbatim. Preserve the meaning of one ACTIVE owner per WRITE SCOPE, independent parallel scopes, stopping the old owner AND its writing processes, preserving and inspecting changes, and assigning the new owner BEFORE writes resume.
Avoid: any remaining Chinese, extra text, new slogans, metrics, option numbers, added objects, file locks, shields, isolation barriers, changed connections, changed layout, watermarks, text overlap or cropping.
```
