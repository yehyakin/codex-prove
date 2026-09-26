# Runtime surface matrix

Release-time evidence for Codex PROVE. Configuration, an agent label, or a child
self-report is not runtime proof. Statuses are `VERIFIED`, `FAILED`, or
`UNVERIFIED`.

Current implementation evidence: 2026-09-26, merged main baseline `936cfca`.

## v1.1 main: four-role implementation

The four-role source is merged into main; the latest stable tag remains v1.0.0.
See [the GPT-6 audit record](v1.1-gpt6-audit.md) for the full chronology.

| Surface | Signal | Status | Evidence location | Date |
| --- | --- | --- | --- | --- |
| Repository | 118 tests and static validation | VERIFIED | Implementation commit `936cfca`; merge-time local suite 24.055 s, exit 0 | 2026-09-26 |
| POSIX CI | Linux/macOS × Python 3.11/3.13 | VERIFIED | main run [36242572791](https://github.com/yehyakin/codex-prove/actions/runs/36242572791), 4/4 jobs successful | 2026-09-26 |
| Windows CI | Windows Server 2022 / windows-latest × PowerShell 5.1/7 | VERIFIED | main run [36242572803](https://github.com/yehyakin/codex-prove/actions/runs/36242572803), 4/4 jobs successful | 2026-09-26 |
| Isolated lifecycle | Four profiles, rollback, unrelated-file preservation, uninstall/restore | VERIFIED | The same CI runs; does not mean a real global installation was upgraded | 2026-09-26 |
| Explicit Astra high launch | Five-request read-only routing sample | VERIFIED | [One evaluation](gpt6-four-role-routing-probe.json), not worker execution or custom-role discovery | 2026-09-26 |
| CLI worker pilot | 18 matched Sol/Terra trials | VERIFIED | [Report](../research/2026-09-25-worker-pilot.md) retains frozen-test results AND post-hoc failures; not a quality/cost winner | 2026-09-25 |
| Current four-role setup | Complete end-to-end runtime | UNVERIFIED | No full current-profile execution record | 2026-09-26 |
| Desktop | Fresh global install / Skill and four-role discovery | UNVERIFIED | Global installation deliberately unchanged by source merge | 2026-09-26 |
| Desktop | Current Native Nested / Compatibility | UNVERIFIED | Earlier model-generation evidence cannot establish the new mapping | 2026-09-26 |
| Physical Windows 11 | Current four-role runtime | UNVERIFIED | Hosted Windows Server CI is not a physical-device runtime test | 2026-09-26 |

The 49 Forward cases are scenario specifications, not 49 live model runs. The
tables below are retained historical evidence, not certification of current
Astra / Sol / Terra / Luna routing. Current branch CI badges may include later
documentation-only commits; the implementation evidence above stays SHA-bound.

## v1.0 model-neutral roles

| Surface | Signal | Status | Evidence location | Date |
| --- | --- | --- | --- | --- |
| Desktop | `prove-controller` selection | VERIFIED | Fresh session `01a01e7c-477a-7a03-9b74-8a7144d6f958`; Host launch plus two-turn handshake and final review | 2026-08-20 |
| Desktop | `prove-complex-worker` selection | VERIFIED | Same fresh session; Host launch plus two-turn handshake | 2026-08-20 |
| Desktop | `prove-efficient-worker` selection | VERIFIED | Same fresh session; Host launch plus two-turn handshake | 2026-08-20 |
| Desktop | exact models and reasoning | VERIFIED | Host/tool mapping and parent launch records: Sol/high, Terra/high, Luna/max | 2026-08-20 |
| Desktop | Native Nested | UNVERIFIED | Requires a real controller-to-worker launch with the new role names | 2026-08-20 |
| Desktop | Compatibility | VERIFIED | Fresh session `01a01e7c-477a-7a03-9b74-8a7144d6f958`; Controller plan, Host worker dispatch, same-Controller final verdict `PASS` | 2026-08-20 |
| Desktop | fresh-session Skill discovery | VERIFIED | Canonical session above; alias session `01a01e81-92bc-7462-bb95-450bc929e971` redirected `$sol-control` to `$codex-prove` | 2026-08-20 |
| Desktop | transactional global install | VERIFIED | Persistent backup `~/.codex/codex-prove/backups/20260820T092316Z-61245`; installed canonical Skill, alias, and three roles | 2026-08-20 |
| POSIX CI | validation and lifecycle | VERIFIED | `main` run [32353507136](https://github.com/yehyakin/codex-prove/actions/runs/32353507136) | 2026-08-20 |
| Windows CI | install/upgrade/rollback/uninstall | VERIFIED | `main` run [32353507150](https://github.com/yehyakin/codex-prove/actions/runs/32353507150), Windows Server 2022 and `windows-latest`, PowerShell 5.1 and 7 | 2026-08-20 |
| Physical Windows 11 | Native Nested | UNVERIFIED | No v1.0 physical-device runtime payload captured | 2026-08-20 |

Update this table only from actual launch, result, lifecycle, or CI evidence.

## Retained v0.5 historical evidence

The previous model-branded release verified the following on 2026-08-17:

- Desktop Host/tool mapping selected `sol-controller`, `terra-high-worker`, and
  `luna-max-worker` with `fork_turns="none"` and the configured model/effort.
- `sol-controller` launched two independent Terra audits, one bounded Luna
  smoke, and one qualifying read-only challenge.
- Host-owned baseline/final snapshots bound changed paths and artifacts before
  the final review.
- A separate `codex exec` Native Nested path proved Sol-to-Luna dispatch and a
  structured worker result.

This evidence supports continuity of the protocol, but it does not prove the new
`prove-*` agent names. The v1.0 release must capture a fresh runtime record.

The matched protocol and retained smoke are documented in
[`tests/v100-ab-benchmark.md`](../../tests/v100-ab-benchmark.md) and
[`tests/v100-live-smoke.md`](../../tests/v100-live-smoke.md). The smoke remains a
single historical pair and does not replace the unfinished full benchmark.
