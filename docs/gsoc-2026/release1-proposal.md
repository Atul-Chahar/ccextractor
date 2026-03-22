# Google Summer of Code 2026 Proposal

## CCExtractor Release 1.00

**Name:** Atul Chahar  
**University:** Medhavi Skills University, India  
**Email:** atulchahar1206@gmail.com  
**GitHub:** https://github.com/Atul-Chahar  
**Timezone:** IST (UTC+5:30)  
**Project size:** 350 hours  

## 1. Summary

Release 1.00 is mostly integration work.

The main job is to help CCExtractor move important open work toward a stable 1.00 release by:

- reviewing and moving release-related PRs
- fixing or clearly classifying regressions
- checking Sample Platform results carefully
- keeping the Flutter GUI aligned with current CLI behavior
- validating the current release path and fixing real gaps

This matches the work I have already been doing in CCExtractor.

I already have merged fixes in CCExtractor, one merged fix in Sample Platform, one open CCExtractor improvement PR, one reported CCExtractor bug, and one review on an open Rust PR.

I also prepared a small proof of work for this proposal:

- POC note: https://github.com/Atul-Chahar/ccextractor/blob/gsoc-release1-poc/docs/gsoc-2026/release1-poc.md
- compare tool: https://github.com/Atul-Chahar/ccextractor/blob/gsoc-release1-poc/tools/compare_ccx_outputs.py

This POC is not a replacement for the Sample Platform or the GitHub bot. It is a small local review helper that compares two binaries on the same sample before deeper CI work.

## 2. Work I Have Already Done

### CCExtractor

- [PR #2079](https://github.com/CCExtractor/ccextractor/pull/2079)  
  Merged on **February 7, 2026**.  
  Fixed empty WebVTT files for HLS compatibility.

- [PR #2147](https://github.com/CCExtractor/ccextractor/pull/2147)  
  Merged on **March 13, 2026**.  
  Fixed an MSVC debug-build invalid free around `output_filename`.

- [PR #2173](https://github.com/CCExtractor/ccextractor/pull/2173)  
  Merged on **March 18, 2026**.  
  Replaced hardcoded `29.97` frame delay math with `current_fps` in the CEA-708 SCC path.

- [PR #2146](https://github.com/CCExtractor/ccextractor/pull/2146)  
  Open as of **March 23, 2026**.  
  Another SCC timecode fix that is still under review.

- [PR #2184](https://github.com/CCExtractor/ccextractor/pull/2184)  
  Open as of **March 23, 2026**.  
  Improves `--out report` so both EIA-608 fields are checked by default.

- [Issue #2172](https://github.com/CCExtractor/ccextractor/issues/2172)  
  Opened by me on **March 4, 2026** and closed on **March 18, 2026** by [PR #2173](https://github.com/CCExtractor/ccextractor/pull/2173).  
  This shows that I also report bugs when I find them.

- Review on [PR #2109](https://github.com/CCExtractor/ccextractor/pull/2109#issuecomment-4002125693)  
  I reviewed the Rust ISDB PR and pointed out a truncated-buffer panic risk in `leaf.rs` and one smaller logic mismatch with the C side.

### Sample Platform

- [PR #1043](https://github.com/CCExtractor/sample-platform/pull/1043)  
  Merged on **March 5, 2026**.  
  Fixed SQLAlchemy test result filtering by replacing a Python identity check with `.is_(False)`.

### Other Open Source Work

My contribution log in `docs/OpenSource Contributions Data.xlsx` also shows recent work in other open source projects, including Keploy, CERT-Polska/Artemis, and GreedyBear.

I mention that only as supporting evidence. The main reason I think I fit this project is the CCExtractor work above.

## 3. Proof Of Work For This Proposal

I built a small compare tool and used it on a real CCExtractor branch.

The full note is here:

- https://github.com/Atul-Chahar/ccextractor/blob/gsoc-release1-poc/docs/gsoc-2026/release1-poc.md

The short version is:

- I upgraded the tool so it can compare stdout-based output such as `--out report`
- I compared `upstream/master` with my open [PR #2184](https://github.com/CCExtractor/ccextractor/pull/2184)
- on the same local `cc3.ts` sample, `master` reported `"cc3": false` and the PR reported `"cc3": true`
- the branch-specific Rust tests for that change passed

This matters because Release 1.00 needs exactly this kind of careful validation work on open PRs.

It also matches the blocker mentioned on [PR #2109](https://github.com/CCExtractor/ccextractor/pull/2109): CCExtractor still needs better regression confidence before some Rust-port PRs can be merged.

## 4. What I Plan To Do

I want to split the work into four practical parts.

### Part 1: Move The Release-Critical PR Backlog

The Release 1.00 idea is mainly about getting important open work reviewed, tested, fixed where needed, and merged.

The open PRs I would expect to discuss first with mentors are:

- [PR #1927](https://github.com/CCExtractor/ccextractor/pull/1927) - Rust SRT encoder
- [PR #2088](https://github.com/CCExtractor/ccextractor/pull/2088) - Rust XDS module
- [PR #2106](https://github.com/CCExtractor/ccextractor/pull/2106) - teletext subtitle fix
- [PR #2109](https://github.com/CCExtractor/ccextractor/pull/2109) - Rust ISDB module
- [PR #2170](https://github.com/CCExtractor/ccextractor/pull/2170) - FFmpeg MP4 demuxing work

I do not want to promise a fixed merge order without mentor input. My first step will be to agree on the order and then work from that list.

For each selected PR, my process will be:

1. read the PR and understand the affected code path
2. build it locally
3. run targeted samples for that feature
4. check Sample Platform results when available
5. fix the problem or explain why the new output is correct
6. move the PR toward merge

### Part 2: Regression Cleanup

Release work needs careful regression handling.

When a PR changes output, I will separate cases into three groups:

- real bug
- correct change that needs a baseline update
- unclear result that needs more discussion or more samples

I will not treat baseline updates as automatic. I will only suggest them when I can explain why the new output is correct.

### Part 3: Keep The Flutter GUI Aligned With The CLI

The Release 1.00 idea also mentions keeping the GUI in sync with the current command-line behavior.

My plan is simple:

- compare important CLI options with the GUI settings that expose them
- test common paths such as normal subtitle extraction and report mode
- fix only real mismatches

### Part 4: Validate The Current Release Path

CCExtractor already has release and packaging workflows.

So my goal here is not to build release automation from scratch. My goal is to check whether the current release path is good enough for 1.00 and fix real blockers if they appear.

That includes:

- reviewing the current release steps
- checking artifact quality on the supported platforms
- writing a clear checklist for the final 1.00 release

## 5. How I Will Validate Results

I want the project to be judged by clear checks.

### For backlog PR work

- the selected PR builds locally
- targeted sample runs make sense
- regressions are fixed or clearly explained
- the PR is merged or left in final-review state with blockers written down

### For regression cleanup

- failing cases are classified one by one
- real bugs get fixes or follow-up patches
- baseline updates are explained before they are accepted

### For GUI work

- the tested GUI paths still call the CLI correctly
- broken option mappings are fixed

### For release work

- the release steps are written down clearly
- the workflows or manual steps needed for 1.00 are tested before final handoff

## 6. Timeline

I wrote this timeline against the official **2026 GSoC schedule**:

- Community bonding: **May 1 - May 24, 2026**
- Coding starts: **May 25, 2026**
- Midterm evaluation window: **July 6 - July 10, 2026**
- Final submission week for standard projects: **August 17 - August 24, 2026**

I also want to be clear about one constraint:

- **June 1 - June 21, 2026:** university exams  
  I can still work during that period, but at about **15 hours per week**.

### Community Bonding: May 1 - May 24

- agree on the release-critical PR order with mentors
- prepare the local review and testing workflow
- review the main open PRs
- confirm what server or sample access I need

**Expected result:** a clear, mentor-approved plan for the coding period.

### Week 1: May 25 - May 31

- start the first priority PR
- build it locally
- run targeted tests
- write down the first fixes or review notes

**Expected result:** first release-related PR actively moving toward merge.

### Weeks 2-4: June 1 - June 21

- keep progress moving during exams with reduced hours
- focus on review work, smaller fixes, and follow-up tasks
- continue work on the first PR and start checking the next one

**Expected result:** steady progress without going silent during the exam period.

### Weeks 5-6: June 22 - July 5

- return to full working hours
- push the first important PR to merge-ready state
- continue with the next priority PR
- check related regressions

**Expected result:** at least one major release-related PR merged or very close to merge.

### Midterm: July 6 - July 10

- present merged work, open fixes, and remaining blockers
- confirm the next priority set with mentors

**Expected result:** clear midterm progress with real code and clear next steps.

### Weeks 7-8: July 11 - July 24

- continue work on the next priority PRs
- fix or classify newly exposed regressions
- document which output changes are real bugs and which are valid updates

**Expected result:** backlog reduced further and regression handling kept under control.

### Weeks 9-10: July 25 - August 7

- continue merge and validation work on the remaining priority PRs
- keep Sample Platform results moving toward a cleaner release state

**Expected result:** most high-priority Release 1.00 work either merged or in final review.

### Weeks 11-12: August 8 - August 16

- check the Flutter GUI against current CLI behavior
- fix real mismatches
- finish release-path validation

**Expected result:** GUI issues found and fixed, and the 1.00 release checklist ready.

### Final Week: August 17 - August 24

- finish final validation
- write the final technical article and work report
- prepare final handoff notes

**Expected result:** Release 1.00 work documented clearly, with code, validation notes, and handoff ready.

## 7. Support I Will Need

From the mentors and CCExtractor team, I expect I will need:

- access to the shared development server
- access to the sample archive or hard-to-find samples when needed
- help deciding the release-critical PR order
- review on tricky baseline-update decisions
- final review on release-path or packaging changes

## 8. Availability And Communication

**Typical working hours:** Monday to Saturday, **10:00-19:00 IST**, which is **04:30-13:30 UTC**

I will stay active on Zulip during the project and keep the mentors updated with short progress notes.

Planned reduced availability:

- **June 1 - June 21, 2026:** about **15 hours per week** because of exams

Planned full absences:

- none right now

## 9. Why I Think I Fit This Project

I think this project fits my current work for simple reasons:

- I already have merged CCExtractor fixes: [PR #2079](https://github.com/CCExtractor/ccextractor/pull/2079), [PR #2147](https://github.com/CCExtractor/ccextractor/pull/2147), and [PR #2173](https://github.com/CCExtractor/ccextractor/pull/2173)
- I already have one merged Sample Platform fix: [PR #1043](https://github.com/CCExtractor/sample-platform/pull/1043)
- I already have one open release-related improvement PR: [PR #2184](https://github.com/CCExtractor/ccextractor/pull/2184)
- I already reviewed one open Rust PR: [PR #2109](https://github.com/CCExtractor/ccextractor/pull/2109#issuecomment-4002125693)
- I am already working across the same mix of C, Rust, and Python that this project needs
- I already built a small validation workflow that can help with PR review work

So this is not a new direction for me. It is a continuation of the work I have already started.

## 10. Other Applications

I am submitting two proposals to **CCExtractor**:

- CCExtractor Release 1.00
- Sample Platform NG

I am **not** applying to other organizations.

## 11. Final Deliverables

If selected, my final work should include:

- merged or merge-ready release-critical PR work
- regression notes with clear bug vs baseline-update decisions
- GUI sync fixes if real mismatches are found
- release-path notes and checklist for 1.00
- the final technical article requested on the ideas page

## 12. References Used For Planning

- CCExtractor 2026 ideas page: https://ccextractor.org/docs/ideas_page_for_summer_of_code_2026/
- Release 1.00 idea page: https://ccextractor.org/public/gsoc/2025/ccextractor_v1/
- GSoC 2026 timeline: https://developers.google.com/open-source/gsoc/timeline
