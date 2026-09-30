#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd -P)
SKILL_ROOT="$ROOT_DIR/.agents/skills/codex-prove"
SKILL_FILE="$SKILL_ROOT/SKILL.md"
OPENAI_FILE="$SKILL_ROOT/agents/openai.yaml"
CONTRACT_FILE="$SKILL_ROOT/references/orchestration.md"
RUNTIME_FILE="$SKILL_ROOT/references/runtime-notes.md"
COMPAT_ROOT="$ROOT_DIR/.agents/skills/sol-control"
COMPAT_SKILL_FILE="$COMPAT_ROOT/SKILL.md"
COMPAT_OPENAI_FILE="$COMPAT_ROOT/agents/openai.yaml"
CONTROLLER_FILE="$ROOT_DIR/.codex/agents/prove-controller.toml"
COMPLEX_FILE="$ROOT_DIR/.codex/agents/prove-complex-worker.toml"
EFFICIENT_FILE="$ROOT_DIR/.codex/agents/prove-efficient-worker.toml"
SPECIALIST_FILE="$ROOT_DIR/.codex/agents/prove-specialist-worker.toml"
WINDOWS_LIFECYCLE_FILE="$ROOT_DIR/tests/windows-lifecycle.ps1"
WINDOWS_WORKFLOW_FILE="$ROOT_DIR/.github/workflows/windows-validation.yml"
POSIX_WORKFLOW_FILE="$ROOT_DIR/.github/workflows/posix-validation.yml"

failures=0
fail() {
  printf 'Validation: FAIL: %s\n' "$1"
  failures=1
}

required_files=(
  ".agents/skills/codex-prove/SKILL.md"
  ".agents/skills/codex-prove/agents/openai.yaml"
  ".agents/skills/codex-prove/references/orchestration.md"
  ".agents/skills/codex-prove/references/runtime-notes.md"
  ".agents/skills/codex-prove/references/ponytail-license.txt"
  ".agents/skills/sol-control/SKILL.md"
  ".agents/skills/sol-control/agents/openai.yaml"
  ".codex/agents/prove-controller.toml"
  ".codex/agents/prove-complex-worker.toml"
  ".codex/agents/prove-efficient-worker.toml"
  ".codex/agents/prove-specialist-worker.toml"
  "scripts/install.sh"
  "scripts/validate.sh"
  "scripts/validate_source.py"
  "scripts/test.sh"
  "scripts/benchmark_ab.py"
  "scripts/uninstall.sh"
  "scripts/install.ps1"
  "scripts/validate.ps1"
  "scripts/uninstall.ps1"
  "README.md"
  "README.en.md"
  "CONTRIBUTING.md"
  "CODE_OF_CONDUCT.md"
  "SECURITY.md"
  "SUPPORT.md"
  ".github/ISSUE_TEMPLATE/bug_report.yml"
  ".github/ISSUE_TEMPLATE/feature_request.yml"
  ".github/ISSUE_TEMPLATE/config.yml"
  ".github/pull_request_template.md"
  ".github/workflows/posix-validation.yml"
  ".github/workflows/windows-validation.yml"
  "docs/assets/readme/hero-zh.svg"
  "docs/assets/readme/hero-en.svg"
  "docs/assets/readme/control-plane-zh.svg"
  "docs/assets/readme/control-plane-en.svg"
  "docs/release/runtime-surface-matrix.md"
  "tests/windows-lifecycle.ps1"
  "tests/fixtures/forward-cases.json"
  "tests/fixtures/v100-ab-benchmark.json"
  "tests/v100-ab-benchmark.md"
  "tests/v100-live-smoke.md"
  "tests/test_v100_benchmark.py"
  "tests/test_v100_evidence_control.py"
  "CODEX_PROVE_V1_IMPLEMENTATION_REPORT.md"
  "NOTICE"
  "LICENSE"
)
for relative in "${required_files[@]}"; do
  [[ -f "$ROOT_DIR/$relative" ]] || fail "missing required file: $relative"
done

for removed in \
  ".agents/skills/sol-luna" \
  ".agents/skills/orchestrate-sol-luna" \
  ".codex/agents/sol-controller.toml" \
  ".codex/agents/terra-high-worker.toml" \
  ".codex/agents/luna-max-worker.toml" \
  ".codex/agents/sol-planner.toml"; do
  [[ ! -e "$ROOT_DIR/$removed" && ! -L "$ROOT_DIR/$removed" ]] || fail "legacy runtime source still exists: $removed"
done

PYTHON_BIN=
for candidate in python3.14 python3.13 python3.12 python3.11 python3 python; do
  candidate_path=$(command -v "$candidate" 2>/dev/null || true)
  if [[ -n "$candidate_path" ]] && "$candidate_path" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' >/dev/null 2>&1; then
    PYTHON_BIN="$candidate_path"
    break
  fi
done
if [[ -z "$PYTHON_BIN" ]]; then
  fail 'Python 3.11 or newer is required'
else
  if ! "$PYTHON_BIN" "$SCRIPT_DIR/validate_source.py" "$ROOT_DIR";
  then
    fail 'source content validation failed; see diagnostic above'
  fi
fi

if command -v ruby >/dev/null 2>&1; then
  if ! ruby -r yaml - "$SKILL_FILE" "$OPENAI_FILE" "$COMPAT_SKILL_FILE" "$COMPAT_OPENAI_FILE" <<'RUBY' >/dev/null 2>&1
paths = ARGV

def load_yaml(text)
  YAML.safe_load(text, permitted_classes: [], permitted_symbols: [], aliases: false)
end

def frontmatter(path)
  lines = File.readlines(path, encoding: "UTF-8")
  raise unless lines.first&.chomp == "---"
  closing = lines[1..].index { |line| line.chomp == "---" }
  raise if closing.nil?
  load_yaml(lines[1, closing].join)
end

canonical = frontmatter(paths[0])
raise unless canonical == {"name" => "codex-prove", "description" => canonical["description"]}
raise unless canonical["description"].include?("$codex-prove")

openai = load_yaml(File.read(paths[1], encoding: "UTF-8"))
raise unless openai.dig("interface", "default_prompt").include?("$codex-prove")
raise unless openai.dig("policy", "allow_implicit_invocation") == false

compat = frontmatter(paths[2])
raise unless compat["name"] == "sol-control" && compat["description"].include?("$sol-control")
compat_openai = load_yaml(File.read(paths[3], encoding: "UTF-8"))
raise unless compat_openai.dig("policy", "allow_implicit_invocation") == false
RUBY
  then
    fail 'YAML parsing or Skill interface validation failed'
  fi
else
  printf 'YAML parser: Ruby unavailable; deterministic structural checks used\n'
fi

for shell_script in "$SCRIPT_DIR/install.sh" "$SCRIPT_DIR/validate.sh" "$SCRIPT_DIR/uninstall.sh" "$SCRIPT_DIR/test.sh"; do
  bash -n "$shell_script" >/dev/null 2>&1 || fail "Bash syntax validation failed: $(basename "$shell_script")"
done

if ! (cd "$ROOT_DIR" && git diff --check -- . >/dev/null 2>&1); then
  fail 'git whitespace validation failed'
fi

PWSH_BIN=$(command -v pwsh 2>/dev/null || true)
if [[ -n "$PWSH_BIN" ]]; then
  if ! PS1_INSTALL_PATH="$SCRIPT_DIR/install.ps1" \
    PS1_VALIDATE_PATH="$SCRIPT_DIR/validate.ps1" \
    PS1_UNINSTALL_PATH="$SCRIPT_DIR/uninstall.ps1" \
    PS1_LIFECYCLE_PATH="$WINDOWS_LIFECYCLE_FILE" \
    "$PWSH_BIN" -NoLogo -NoProfile -NonInteractive -Command '
      foreach ($path in @($env:PS1_INSTALL_PATH, $env:PS1_VALIDATE_PATH, $env:PS1_UNINSTALL_PATH, $env:PS1_LIFECYCLE_PATH)) {
        $tokens = $null; $errors = $null
        [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors) | Out-Null
        if ($errors.Count -gt 0) { exit 1 }
      }
    ' >/dev/null 2>&1; then
    fail 'PowerShell AST parsing failed'
  fi
else
  printf 'PowerShell: pwsh unavailable; deterministic structural checks used\n'
fi

if (( failures != 0 )); then
  printf 'Validation: FAIL\n'
  exit 1
fi
printf 'Validation: PASS\n'
