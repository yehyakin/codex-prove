# README integration check

Checked 2026-10-01–02, Asia/Shanghai. Local worktree only; not committed, pushed, or released.

## Integrated content

- Chinese and English root READMEs use the reviewed cost-budget, routing, evidence, and ownership PNGs. Ownership is in a collapsed detail; GIFs are optional links.
- The 82.8% calculation compares 64.5 credits with an all-Astra baseline of 375. The 3.75-credit overhead remains 5% of all-Sol, not 5% of all-Astra. Both languages label the budget as illustrative, not measured.
- Cost notes include the dated Standard rate extract, equal token-volume assumptions, calculation, and exclusions. Historical budgets and runtime receipts retain their original scope.
- Image pixels and render receipts were not changed. Only the selected asset manifests' integration status changed.

## Fresh checks

| Check | Result |
| --- | --- |
| README tests, including legacy SVG contracts | 24 passed |
| Full repository unit suite | 135 passed, exit 0 |
| Source validator and whitespace check | Passed |
| Classic, polish, cost, cost-budget source/asset validators | All passed |
| Chinese and English local preview | Images loaded, language links and page anchors worked |
| 1440 × 1080 and 390 × 844 viewports | Page width equalled viewport width; no horizontal page overflow |
| Ownership detail | Initially collapsed; opened successfully in both languages |
| Browser console | 0 errors, 0 warnings |

The first full-suite run had seven failing assertions because the source-test fixture recursively excluded every directory named `media`, including linked documentation sources. The fixture now copies tracked and non-ignored source files, keeps documentation media, and retains the root scratch-media exclusion. The validation rules were not relaxed; the rerun passed all 135 tests. Local render outputs and dependencies are not copied into that fixture.

The visual validator still compares runtime instructions and model profiles byte-for-byte with the committed baseline. README and cost-note integration preserves the archived snapshots and checks every cited excerpt in both archived and current documents, recording separate hashes. Current README model mappings, budget math, rates, asset hashes, and links are checked by the document tests.

## Scope and limits

The browser rendered the actual Markdown using a local renderer and GitHub-like CSS, not GitHub's hosted renderer. PNG details shrink on phones, so the numerical assumptions and workflow facts also remain in selectable body text. The preview used a loopback-only, allowlisted temporary server; browser captures are under `output/playwright/readme-integration/` and excluded from Git.

This is documentation/layout verification, not a new live-agent run, a cost or quality A/B study, or release acceptance. PowerShell was unavailable locally; the source validator used structural checks, and no new Windows runtime result is claimed.
