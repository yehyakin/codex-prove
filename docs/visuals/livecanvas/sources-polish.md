# Selected-series sources and asset provenance

Checked 2026-10-01, Asia/Shanghai. Facts are anchored to candidate commit
`f4dba1c20b0dc299fbcf565bc883c5afdc0324a9`, not the released version.

## Factual sources

1. [Candidate README](https://github.com/yehyakin/codex-prove/blob/f4dba1c20b0dc299fbcf565bc883c5afdc0324a9/README.md):
   the four routing choices and their scope.
2. [Candidate skill](https://github.com/yehyakin/codex-prove/blob/f4dba1c20b0dc299fbcf565bc883c5afdc0324a9/.agents/skills/codex-prove/SKILL.md):
   one active write-scope owner, safe handoff order, actual-evidence review and
   PASS/FIX/BLOCKED meanings.

The local files were read directly and compared to those committed snapshots.
`data-polish.json` contains ten claims with exact source excerpts.
`validate.mjs --series=polish` checks source identity, excerpts and reviewed-asset
hashes. This structural check does not independently read text from the PNGs.

## Artwork

The Chinese routing master is the first displayed Product Design image selected
by the user. Two additional subjects extend its visual direction. Each has an
English translation edition: three subjects, not six distinct topics.

All six posters are generated illustrations, not official screenshots, logos,
runtime traces, benchmark measurements or evidence of a real passing run.
No stock images were used. New source images reference existing project artwork.
No claim of third-party stock licensing or guaranteed copyright protection is made.

Exact prompts and portable generation references:

- [Routing](public/media/polish/routing-prompts.md)
- [Ownership](public/media/polish/ownership-prompts.md)
- [Evidence](public/media/polish/evidence-prompts.md)

The text is baked into the source posters. Remotion exposes the visibility
sequence, timing and composition; it does not expose separate editable text layers.

## Inherited toolchain

Same pinned LiveCanvas workflow and Remotion 4.0.530 dependencies as the original
series. [Original toolchain and license notes](sources.md) still apply.
The implementation preserves their MIT notices and the separate Remotion license.
No global skill installation, new service, cloud publishing or account action.

## Outputs and limits

PNG/JPEG covers, GIF/MP4 previews and paired `.pvt` resource packages are separate
formats. ZIP is transport only. Local metadata and PHLivePhoto checks are not
evidence of iPhone, Photos import, lock-screen or social-platform compatibility.
