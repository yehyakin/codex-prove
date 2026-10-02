# Cost budget prompts

Provider: OpenAI built-in imagegen, not CLI/API fallback.

## Chinese edit

Use case: productivity-visual
Asset type: Codex PROVE cost-budget comparison poster, landscape 16:9.
Input images: Image 1 is the edit target and visual-style reference.
Primary request: update this cost-mechanism poster into the user-approved illustrative cost comparison against all GPT-6 Astra. Preserve the dark navy background, restrained orange/mint/lavender glow, crisp large typography, top-left P mark and CODEX PROVE wordmark, outer margins and overall premium engineering-poster visual language. Replace the old mechanism diagram and all old explanatory copy with the precise budget content below. Keep an opaque background.
Composition: left half is a large headline with the 82.8% figure; right half contains two vertically stacked, equal-sized comparison cards. The upper card is Astra with the existing simple lavender star motif. The lower card is Sol 6.1 + Luna with a simple orange sun and mint small gear motif. A thin connection between them suggests comparison, not execution order. Card area must NOT encode cost; do not draw proportion bars, pie charts, towers, coins, or banknotes. This is a credits-budget example, not measured task performance. Use ample whitespace and legible footer text.
Text (verbatim; no extra words):
Top-left: "CODEX PROVE"
Top-right: "成本预算示例"
Left small heading: "预计节省"
Left primary, largest: "82.8%"
Left subtitle: "相对全程 Astra"
Upper right card: "全程 Astra" and "375 credits" and "100% 基线"
Lower right card: "Sol 6.1 + Luna" and "64.5 credits" and "17.2% 预算"
Bottom explanatory line 1: "示例分工：Sol 6.1 80% · Luna 20%"
Bottom explanatory line 2: "100 万非缓存输入 + 10 万输出 tokens · 另计 3.75 credits 协调开销"
Footer: "预算示例，非实测 · 比例非固定配额 · Standard · 2026-10-01"
Constraints: all values and Chinese glyphs must be exact; the 82.8% number must remain attached to the forecast qualifier and Astra comparison. Do not claim measured savings or guaranteed quality. No extra logos, third-party marks, watermarks, historical 62.3%, or all-Sol baseline. Output a polished horizontal poster matching the reference quality.

## English localization

Use case: text-localization
Asset type: English localization of the approved Codex PROVE cost-budget comparison poster.
Input images: Image 1 is the Chinese poster to edit.
Primary request: replace only Chinese copy with the English equivalents specified below. Preserve the exact canvas, layout, same-size cost cards, typography hierarchy, navy background, orange/mint/lavender accents, thin comparison connection, icons, margins, and every numeric value. Keep the top-left P mark and CODEX PROVE unchanged. Keep an opaque background. Natural readable line wrapping is allowed within the same regions.
Text replacements (verbatim):
"成本预算示例" -> "ILLUSTRATIVE BUDGET"
"预计节省" -> "Estimated savings"
"82.8%" remains "82.8%"
"相对全程 Astra" -> "vs. all-Astra"
"全程 Astra" -> "All-Astra"
"375 credits" remains "375 credits"
"100% 基线" -> "100% baseline"
"Sol 6.1 + Luna" remains "Sol 6.1 + Luna"
"64.5 credits" remains "64.5 credits"
"17.2% 预算" -> "17.2% budget"
"示例分工：Sol 6.1 80% · Luna 20%" -> "Example split: Sol 6.1 80% · Luna 20%"
"100 万非缓存输入 + 10 万输出 tokens · 另计 3.75 credits 协调开销" -> "1M uncached input + 0.1M output tokens · +3.75 credits coordination"
"预算示例，非实测 · 比例非固定配额 · Standard · 2026-10-01" -> "Illustrative, not measured · Not fixed quotas · Standard · 2026-10-01"
Constraints: no other changes, no additional claims, no numbers removed, no text cropped. Card size is decorative and must not be turned into proportional cost bars.
