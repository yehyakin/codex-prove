#!/usr/bin/env python3
"""Protect README facts and usability without freezing marketing prose."""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
import unittest
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
READMES = (ROOT / "README.md", ROOT / "README.en.md")
COSTS = ROOT / "docs/costs.md"
REPO = "https://github.com/yehyakin/codex-prove"
LINK_RE = re.compile(r"!?\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
RATES = {
    "GPT-6 Astra": ("10.00", "1.00", "50.00", "250", "25", "1,250"),
    "GPT-6 Sol": ("2.00", "0.20", "10.00", "50", "5", "250"),
    "GPT-5.6 Terra": ("2.00", "0.20", "12.00", "50", "5", "300"),
    "GPT-6 Luna": ("0.10", "0.01", "0.50", "2.5", "0.25", "12.5"),
}
OLD_RATES = {
    "GPT-5.6 Sol": ("5.00", "0.50", "30.00", "125", "12.5", "750"),
    "GPT-5.6 Terra": ("2.00", "0.20", "12.00", "50", "5", "300"),
    "GPT-5.6 Luna": ("0.20", "0.02", "1.20", "5", "0.5", "30"),
}
SCENARIOS = (
    ("0.10", "0.20", "0.70", "0.03", "0.07", "72.2", "76.2"),
    ("0.20", "0.40", "0.40", "0.02", "0.12", "50.4", "60.4"),
    ("0.25", "0.60", "0.15", "0.07", "0.17", "33.4", "43.4"),
)


def visible_markdown(text: str) -> str:
    lines, fence = [], None
    for line in text.splitlines():
        if fence:
            if re.fullmatch(rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}\s*", line):
                fence = None
            lines.append("")
            continue
        opening = re.match(r" {0,3}(" + chr(96) + r"{3,}|~{3,})", line)
        if opening:
            fence = opening[1]
            lines.append("")
        else:
            lines.append(line)
    return re.sub(r"<!--.*?-->", "", "\n".join(lines), flags=re.S)


def heading_ids(text: str) -> set[str]:
    counts, ids = {}, set()
    for title in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", visible_markdown(text), re.M):
        slug = re.sub(r"[^\w -]", "", re.sub(r"<[^>]*>", "", title).lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        ids.add(f"{slug}-{count}" if count else slug)
        counts[slug] = count + 1
    return ids


def table_rows(text: str) -> list[tuple[str, ...]]:
    return [tuple(c.strip() for c in line.strip().strip("|").split("|"))
            for line in visible_markdown(text).splitlines() if line.strip().startswith("|")]


def link_errors(path: Path, text: str) -> list[str]:
    errors = []
    visible = visible_markdown(text)
    links = [m[1] or m[2] for m in LINK_RE.finditer(visible)]
    links += re.findall(r'<(?:a|img)\b[^>]*\b(?:href|src)="([^"]+)"', visible)
    for link in links:
        parsed = urlsplit(link.replace("&amp;", "&"))
        if parsed.scheme or parsed.netloc:
            continue
        target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
        if not target.is_relative_to(ROOT.resolve()):
            errors.append(f"outside repository: {link}")
        elif not target.is_file():
            errors.append(f"missing file: {link}")
        elif parsed.fragment and target.suffix == ".md":
            if unquote(parsed.fragment) not in heading_ids(target.read_text(encoding="utf-8")):
                errors.append(f"missing heading: {link}")
    return errors


class ReadmeContractTests(unittest.TestCase):
    def documents(self):
        return {path: path.read_text(encoding="utf-8") for path in READMES}

    def test_language_switches(self):
        for text in self.documents().values():
            for link in ("[简体中文](README.md)", "[English](README.en.md)"):
                self.assertIn(link, "\n".join(text.splitlines()[:8]))
        notes = COSTS.read_text(encoding="utf-8")
        for value in ("## English", "(../README.md)", "(../README.en.md)"):
            self.assertIn(value, notes)

    def test_link_helpers(self):
        fence = chr(96) * 3
        fixture = f"{fence}md\n![hidden](missing.svg)\n{fence}\n<!-- ![hidden](other.svg) -->\n![visible](real.svg)"
        self.assertEqual([("visible", "real.svg")], IMAGE_RE.findall(visible_markdown(fixture)))
        self.assertEqual([], IMAGE_RE.findall(visible_markdown(f"~~~~md\n{fence}\n![hidden](nested.svg)\n~~~~")))
        self.assertEqual({"能省多少", "whats-new", "repeat", "repeat-1"},
                         heading_ids("# 能省多少\n## What's new?\n## Repeat\n## Repeat"))
        for fixture in ("[bad](missing.md)", "[bad](../outside.md)", "[bad](README.md#missing-heading)", '<a href="missing.md">bad</a>'):
            self.assertTrue(link_errors(READMES[0], fixture), fixture)

    def test_relative_links_and_anchors(self):
        for path in (*READMES, COSTS):
            self.assertEqual([], link_errors(path, path.read_text(encoding="utf-8")), path.name)

    def test_repository_images_and_folds(self):
        for (path, text), lang in zip(self.documents().items(), ("zh", "en")):
            self.assertIn(REPO, text)
            self.assertNotRegex(text, r"https://github\.com/yehyakin/(?:codex-sol-luna|sol-control)")
            images = IMAGE_RE.findall(visible_markdown(text))
            self.assertEqual([f"docs/assets/readme/hero-{lang}.svg", f"docs/assets/readme/control-plane-{lang}.svg"],
                             [target for _, target in images])
            self.assertTrue(all(alt.strip() for alt, _ in images))
            self.assertEqual(text.count("<details>"), text.count("</details>"))

    def test_model_names_match_configuration(self):
        for label, profile in (
            ("GPT-6 Astra", "prove-controller"), ("GPT-6 Sol", "prove-specialist-worker"),
            ("GPT-5.6 Terra", "prove-complex-worker"), ("GPT-6 Luna", "prove-efficient-worker"),
        ):
            config = tomllib.loads((ROOT / f".codex/agents/{profile}.toml").read_text(encoding="utf-8"))
            self.assertEqual(label.lower().replace(" ", "-"), config["model"])
            for path, text in self.documents().items():
                self.assertEqual(1, sum(r[0] == label for r in table_rows(text)), f"{path.name}: {label}")

    def test_homepage_prices_and_assumptions(self):
        for path, text in self.documents().items():
            for row in table_rows(text):
                if row[0] in RATES:
                    rate = RATES[row[0]]
                    self.assertEqual(("$" + rate[0], "$" + rate[2]), row[-2:])
            for fact in ("2026-09-26", "Standard", "1M", "0.1M", "20% / 20% / 40% / 20%", "5%", "docs/costs.md"):
                self.assertIn(fact, text, path.name)

    def test_budget_has_nearby_context(self):
        patterns = (
            ("预算例子", "不是每个项目", "不含人工和等待时间", "返工", "也可能更贵"),
            ("budget example", "not a promise", "not your time or the wait", "rework", "more expensive"),
        )
        for (path, text), required in zip(self.documents().items(), patterns):
            section = next(s for s in re.split(r"(?m)^## ", visible_markdown(text)) if "$15.00" in s)
            for value in ("$15.00", "$5.66", "62.3%", "docs/costs.md", *required):
                self.assertIn(value, section, path.name)

    def test_cost_comparison_table_matches_the_budget_example(self):
        for path, text in self.documents().items():
            comparisons = [row for row in table_rows(text) if len(row) == 4 and row[1] in ("$15.00", "$5.66")]
            self.assertEqual(2, len(comparisons), path.name)
            baseline, routed = comparisons
            self.assertIn("Astra", baseline[0])
            self.assertIn("PROVE", routed[0])
            self.assertEqual(("$15.00", "375", "—"), baseline[1:])
            self.assertEqual(("$5.66", "141.5", "62.3%"), tuple(cell.strip("*") for cell in routed[1:]))
            for column in (1, 2):
                saving = (1 - Decimal(routed[column].lstrip("$")) / Decimal(baseline[column].lstrip("$"))) * 100
                self.assertEqual(Decimal("62.3"), saving.quantize(Decimal("0.1")))

    def test_current_rates_and_sources(self):
        current = COSTS.read_text(encoding="utf-8").split("## v1.0")[0]
        for model, values in RATES.items():
            self.assertIn((model, *("$" + v if i < 3 else v for i, v in enumerate(values))), table_rows(current))
        for value in (
            "https://developers.openai.com/api/docs/pricing",
            "https://developers.openai.com/api/docs/models/gpt-5.6-terra",
            "https://learn.chatgpt.com/docs/pricing", "2026-09-26", "272K", "Standard", "1.25×", "2×", "2.5×",
        ):
            self.assertIn(value, current)

    def test_current_budget_math(self):
        shares = tuple(map(Decimal, ("0.2", "0.2", "0.4", "0.2")))
        output = Decimal("0.1")
        api = [Decimal(r[0]) + output * Decimal(r[2]) for r in RATES.values()]
        credits = [Decimal(r[3]) + output * Decimal(r[5].replace(",", "")) for r in RATES.values()]
        routed = sum(s * cost for s, cost in zip(shares, api))
        total = routed + Decimal("0.05") * api[0]
        credit_total = sum(s * cost for s, cost in zip(shares, credits)) + Decimal("0.05") * credits[0]
        saving = ((1 - total / api[0]) * 100).quantize(Decimal("0.1"))
        self.assertEqual((Decimal(1), Decimal("15"), Decimal("4.91"), Decimal("5.66"), Decimal("141.5"), Decimal("62.3")),
                         (sum(shares), api[0], routed, total, credit_total, saving))
        notes = COSTS.read_text(encoding="utf-8")
        for fact in ("$15.00", "$4.91", "$0.75", "$5.66", "62.3%", "375 → 141.5 credits"):
            self.assertIn(fact, notes)

    def test_cost_notes_distinguish_billing_time_and_quality(self):
        notes = COSTS.read_text(encoding="utf-8")
        for value in (
            "不代表订阅月费", "每周可用额度", "人工成本", "等待时间", "not routing quotas, observed averages, or a guarantee",
            "subscription price", "weekly usage", "human effort and elapsed time", "don't add the example's 5% again",
            "not establish equal output quality", "不适用于当前", "do not apply to the current four-model setup",
        ):
            self.assertIn(value, notes)

    def test_historical_prices_retained_outside_homepage(self):
        history = COSTS.read_text(encoding="utf-8").split("## v1.0", 1)[1]
        self.assertIn("2026-08-04", history)
        for model, values in OLD_RATES.items():
            self.assertIn((model, *("$" + v for v in values[:3])), table_rows(history))
            self.assertIn((model, *(v + " credits" for v in values[3:])), table_rows(history))
        for text in self.documents().values():
            for claim in ("72.2%–76.2%", "50.4%–60.4%", "33.4%–43.4%"):
                self.assertNotIn(claim, text, "Old savings must not imply GPT-6 results")
        for source in ("https://developers.openai.com/api/docs/models/compare", "https://help.openai.com/en/articles/20001106-codex-rate-card"):
            self.assertIn(source, history)

    def test_historical_scenario_math(self):
        rows = table_rows(COSTS.read_text(encoding="utf-8"))
        for scenario in SCENARIOS:
            sol, terra, luna, low, high, saving_low, saving_high = map(Decimal, scenario)
            self.assertEqual(Decimal(1), sol + terra + luna)
            cost = sol + terra * Decimal("0.40") + luna * Decimal("0.04")
            self.assertEqual(saving_low, (1 - cost - high) * 100)
            self.assertEqual(saving_high, (1 - cost - low) * 100)
            shares = f"Sol {sol * 100:.0f}% · Terra {terra * 100:.0f}% · Luna {luna * 100:.0f}%"
            overhead = f"{low * 100:.0f}%–{high * 100:.0f}%"
            savings = f"{saving_low}%–{saving_high}%"
            self.assertTrue(any(r[1:] == (shares, overhead, savings) for r in rows))

    def test_platform_commands(self):
        for path, text in self.documents().items():
            for command in (
                f"git clone {REPO}.git", "cd codex-prove", "Set-Location codex-prove", "Python 3.11+",
                "bash scripts/validate.sh", "bash scripts/install.sh", "bash scripts/uninstall.sh",
                "bash scripts/uninstall.sh --restore-latest", "git status --short", "git switch main", "git pull --ff-only origin main",
            ):
                self.assertIn(command, text, path.name)
            for script in ("validate", "install", "uninstall"):
                self.assertIn(f"powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/{script}.ps1", text)
                self.assertIn(f"pwsh -NoProfile -File scripts/{script}.ps1", text)
                self.assertTrue((ROOT / f"scripts/{script}.ps1").is_file())
            self.assertIn("scripts/uninstall.ps1 -RestoreLatest", text)

    def test_activation_and_simple_tasks(self):
        patterns = (
            (r"只有你写了.*\$codex-prove.*才会启用", r"简单任务.*不额外开子代理", r"默认用简体中文"),
            (r"only runs when you ask for.*\$codex-prove", r"small tasks stay direct, without extra agents", r"Simplified Chinese by default"),
        )
        for text, required in zip(self.documents().values(), patterns):
            for pattern in required:
                self.assertRegex(text, pattern)
            self.assertIn("$sol-control", text)

    def test_user_files_and_release_status(self):
        patterns = (
            (r"不改.*config.toml", r"不动其他 Agent", r"先备份", r"不会直接覆盖"),
            (r"config.toml.*alone", r"doesn't touch unrelated agents", r"backs up", r"instead of overwriting"),
        )
        for text, required in zip(self.documents().values(), patterns):
            for pattern in required:
                self.assertRegex(text, pattern)
            for value in (f"{REPO}/releases/tag/v1.1.0", "docs/release/v1.1.0.md", "docs/release/runtime-surface-matrix.md", "docs/release/v1.1-gpt6-audit.md"):
                self.assertIn(value, text)

    def test_runtime_history_stays_in_linked_docs(self):
        matrix = (ROOT / "docs/release/runtime-surface-matrix.md").read_text(encoding="utf-8")
        current, history = matrix.split("## v1.0 model-neutral roles", 1)
        for value in ("936cfca", "118", "36242572791", "36242572803", "49", "18", "gpt6-four-role-routing-probe.json"):
            self.assertIn(value, current)
        live = current.split("## 2026-09-26 implementation baseline", 1)[0]
        statuses = {
            "Complete end-to-end runtime": "VERIFIED",
            "Compatibility (explicit-profile)": "VERIFIED",
            "Global installation": "VERIFIED",
            "Installed Skill discovery and Direct": "VERIFIED",
            "Four-role declaration discovery": "VERIFIED",
            "Native Nested": "UNVERIFIED",
            "Current four-role runtime": "UNVERIFIED",
        }
        for surface, expected_status in statuses.items():
            matching = [r for r in table_rows(live) if len(r) >= 3 and r[1] == surface]
            self.assertEqual(1, len(matching), surface)
            self.assertEqual(expected_status, matching[0][2])
        receipt = json.loads((ROOT / "docs/release/v1.1.0-runtime.json").read_text(encoding="utf-8"))
        self.assertEqual("v1.1.0", receipt["release"])
        for relative, expected_hash in receipt["source_runtime_sha256"].items():
            source_bytes = (ROOT / relative).read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(expected_hash, hashlib.sha256(source_bytes).hexdigest(), relative)
        self.assertEqual(4, len(receipt["runtime"]["launches"]))
        for launch in receipt["runtime"]["launches"]:
            profile = tomllib.loads((ROOT / f'.codex/agents/{launch["profile"]}.toml').read_text(encoding="utf-8"))
            self.assertEqual((profile["model"], profile["model_reasoning_effort"]),
                             (launch["model"], launch["reasoning_effort"]))
        self.assertEqual("Compatibility", receipt["runtime"]["execution_mode"])
        self.assertEqual("PASS", receipt["runtime"]["controller_verdict"])
        self.assertEqual(0, receipt["smoke"]["exit_code"])
        self.assertEqual(0, receipt["fresh_session"]["direct"]["spawn_count"])
        self.assertTrue(receipt["fresh_session"]["direct"]["expected_bytes_verified"])
        self.assertTrue(receipt["smoke"]["user_change_preserved"])
        self.assertIn("| Desktop | Compatibility | VERIFIED |", history)
        self.assertIn("| Desktop | Native Nested | UNVERIFIED |", history)

    def test_support_security_and_prior_art(self):
        for path, text in self.documents().items():
            for link in (
                "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "SUPPORT.md", "LICENSE", "NOTICE",
                "https://github.com/yehyakin", f"{REPO}/security/advisories/new", f"{REPO}/issues/new/choose",
                ".agents/skills/codex-prove/SKILL.md", ".agents/skills/codex-prove/references/orchestration.md",
                ".agents/skills/codex-prove/references/runtime-notes.md",
                "https://github.com/DietrichGebert/ponytail", "https://github.com/obra/superpowers",
            ):
                self.assertIn(link, text, path.name)

    def test_linux_do_thanks_is_last(self):
        thanks = (
            "感谢 [LINUX DO 论坛](https://linux.do/) 社区的关注、反馈与支持",
            "Thank you to the [LINUX DO forum](https://linux.do/) community for its attention, feedback, and support.",
        )
        for (path, text), sentence in zip(self.documents().items(), thanks):
            self.assertTrue(text.rstrip().endswith("**致谢 / Thanks**\n\n" + sentence), path.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
