# Release 1.00 POC: Local Validation For Review Work

## Goal

This POC is a small local review helper for comparing two CCExtractor binaries on the same sample.

It is **not** a replacement for the Sample Platform or the GitHub bot. It is a smaller first step that helps a reviewer check one branch against `master` before deeper CI work.

That makes it relevant to the Release 1.00 idea and also to the blocker mentioned on [PR #2109](https://github.com/CCExtractor/ccextractor/pull/2109), where better regression validation is needed before Rust-port PRs can be merged with confidence.

## Files In This POC

- [`tools/compare_ccx_outputs.py`](https://github.com/Atul-Chahar/ccextractor/blob/gsoc-release1-poc/tools/compare_ccx_outputs.py)
- [`docs/gsoc-2026/release1-poc.md`](https://github.com/Atul-Chahar/ccextractor/blob/gsoc-release1-poc/docs/gsoc-2026/release1-poc.md)

## What The Tool Does

The tool runs two CCExtractor binaries with the same input and the same arguments, then records:

- the exact command used for each run
- exit codes
- SHA-256 hashes and sizes
- a unified diff for text outputs

It supports two cases:

1. normal file output such as `srt`, `ttxt`, or `vtt`
2. stdout-based output such as `--out report`

The second case matters for review work because `--out report` does not create an output file. It prints the report to stdout instead.

## Real Case Study Used For This Proposal

I used the tool on my open [PR #2184](https://github.com/CCExtractor/ccextractor/pull/2184), which changes `--out report` so both EIA-608 fields are checked by default.

Compared builds:

- baseline: `upstream/master` at `03ad9e8e029ded37980c8b51f8c9450aedc5a6e5`
- candidate: PR `#2184` head at `63a9f30819f43cb71477e68cf5b05a00a2f68825`

Build command used in both worktrees:

```bash
cmake ../src -DWITH_OCR=OFF -DWITH_HARDSUBX=OFF
cmake --build . -j4
```

Sample used:

- local file: `cc3.ts`
- file type: MPEG transport stream
- SHA-256: `e8999073f72c98f653287d86f1a4233972d19d2cd249c040a2598d10aa422040`

I did not add this sample to the repo. It was only used as a local validation sample for the proposal.

## Command Used

```bash
python tools/compare_ccx_outputs.py \
  --base-binary /tmp/ccextractor-proposal-poc-20260323/build/ccextractor \
  --candidate-binary /tmp/ccextractor-pr2184/build/ccextractor \
  --input /home/omarchy/OpenSource/ccextractor/ccextractor/cc3.ts \
  --stdout-as-output \
  --arg=--out \
  --arg=report \
  --arg=--report-format \
  --arg=json \
  --output-dir /tmp/ccextractor-poc-run-tool-1
```

## Observed Result

The tool reported:

- same exit code: `true`
- same stdout SHA-256: `false`
- stdout diff present: `true`

The diff was:

```diff
--- base.log
+++ candidate.log
@@ -37,7 +37,7 @@
            "channels": {
              "cc1": false,
              "cc2": false,
-             "cc3": false,
+             "cc3": true,
              "cc4": false
            }
```

This is the important point of the case study:

- `master` missed `cc3` on this sample in report mode
- PR `#2184` detected `cc3`

That is a real before/after difference on the same stream, produced by the local compare workflow.

## Extra Verification

The branch-specific Rust parser tests for this change passed:

```bash
cargo test -p ccx_rust test_out_report_
```

Result:

- `test_out_report_enables_file_reports` passed
- `test_out_report_with_stdout_no_conflict` passed

## Why This Helps The Release 1.00 Project

Release 1.00 is mostly review, validation, and integration work. A small local tool like this is useful because it gives a reviewer a quick first check before relying on the full Sample Platform flow.

For example, the same approach can be reused on open release-related PRs such as:

- [PR #2109](https://github.com/CCExtractor/ccextractor/pull/2109)
- [PR #2106](https://github.com/CCExtractor/ccextractor/pull/2106)
- [PR #1927](https://github.com/CCExtractor/ccextractor/pull/1927)
- [PR #2088](https://github.com/CCExtractor/ccextractor/pull/2088)

That is why I am including this as POC for the proposal. It is small, but it is directly connected to the kind of work the project actually needs.
