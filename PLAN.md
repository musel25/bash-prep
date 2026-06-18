# Plan — bash-prep

## Goal

Drilling Bash + Unix command-line fundamentals to pass technical screens — reach the point
where I can read a pipeline and know what it does, write a basic command without guessing,
and not get blindsided by the classic gotchas.

**Target screen:** Modal — Forward Deployed Engineer (ML). ~2 weeks out (interview week of
~2026-06-29 / early July). Format: they show short snippets / command lines and I *talk
through* them out loud — what they do, edge cases, how I'd improve/test them. No AI in the
room. They named Bash specifically: reading pipelines + **basic process / file-permission
concepts** + **basic concurrency/performance intuition (high level)**. (Python/JS prepped
elsewhere; this repo is the Bash slice.)

**Shape (revised 2026-06-18):** Pre-built **exercise bank**, then drill it interactively.
The whole roadmap is written to the repo up front so I can *see* every exercise. Each topic
folder has a tight **cheat-sheet intro** (command → flag → what it does), the **classic
gotchas**, and a set of **exercises** — half *read* ("what does this do / print?"), half
*write* ("how would you …?"). Answers live in a separate `answers.md` so questions aren't
spoiled, and every "what does this print" answer is **verified by actually running it in
bash** (evidence over assertion). After the 7 topic banks, a **mock bank** of random
Modal-style snippets drawn from real interview experiences.

> This deliberately overrides the original "no big-bang scaffolding / one slice at a time"
> rule — I asked to see the full map up front. We still drill interactively (explain-back,
> no bluffing); the bank is just visible ahead of time instead of revealed live.

**How we drill each topic:** I read the intro, attempt the exercises out loud / in writing,
*then* check `answers.md`. Interview reps (read → explain → edge case → how to test) are the
exercise format itself, not an add-on.

## Repo layout

```
slices/NN-topic/README.md    cheat-sheet intro + gotchas + exercises (no answers)
slices/NN-topic/answers.md   answer key with real verified bash output
mock/modal-style.md          random Modal-style mixed snippets (questions)
mock/answers.md              answer key for the mock bank
```

## Slices

> Ordered by risk + payoff. Each = short notes + real executed examples + a few drills,
> ending with explain-back. **Every drill runs in real `bash`, never interactive zsh.**

- [ ] **Slice 1 — Pipes & redirection.** `|`, `>`, `>>`, stdin/stdout/stderr, the `2>&1`
      ordering trap. _Highest-frequency screen topic._
- [ ] **Slice 2 — Quoting & word-splitting.** `"$x"` vs `$x`, globbing, command
      substitution. _#1 source of broken scripts._
- [ ] **Slice 3 — Exit codes & conditionals.** `$?`, `&&`/`||`, `if`, `[ ]` vs `[[ ]]`,
      `-eq` vs `==`, `set -euo pipefail`.
- [ ] **Slice 4 — Find & filter.** `grep` deeper, `find` + `-exec` vs `xargs`, the
      `sort | uniq` adjacency trap.
- [ ] **Slice 5 — Text processing.** `cut`, `tr`, enough `sed`/`awk` to read them.
- [ ] **Slice 6 — Permissions, processes & concurrency.** _(NEW — Modal named these.)_
      `chmod`/octal bits (read `script.sh`'s `751`), `ps`/`kill`/signals basics, `&` + `wait`,
      `xargs -P`, "why a loop spawning processes is slow" perf intuition.
- [ ] **Slice 7 — Variables & a real script.** shebang, `$1`/`$@`, loops — tie it together
      in one script I write.

**Current slice:** Slice 1 — Pipes & redirection.

## Decisions

- **Shape = Teach → drill ladder** (not a pure drill bot). I start near zero, so I need the
  concept and the *why* before reps would mean anything.
- **All drills run in real `bash`** (`bash script.sh` / `#!/usr/bin/env bash`), never the
  interactive zsh prompt — zsh and bash differ on word-splitting, exactly the slice-2 topic.

## Not building yet

- No automated drill/scoring bot — premature before the concepts land.
- No advanced `awk`/`sed` programming, regex deep-dive, or `sed` scripting (slice 5 stays
  "enough to read it").
- No process *substitution* or `trap` handlers — still niche for this screen. _(Reversed from
  the original plan: basic signals + background jobs are now IN, slice 6, because Modal named
  process/concurrency concepts directly.)_

## Open unknowns

- ~~Target timeline / screen format~~ — RESOLVED: Modal FDE-ML, ~2 weeks, reading-focused.
- **Can I reason about edge cases out loud, not just run commands?** That's the whole
  interview. Not a spike — tested continuously by the interview overlay, from slice 1.

## Log

> Append-only. One line per session: date — what got proven.

- 2026-06-17 — Project mapped: goal + 6 slices + shape decided. No code yet.
- 2026-06-18 — Re-mapped for the real target (Modal FDE-ML, ~2wk, reading-focused). Added
  interview overlay + Slice 6 (permissions/processes/concurrency); signals/bg-jobs pulled
  back in. Now 7 slices. Still no code — slice 1 next.
- 2026-06-18 — Started drilling Slice 1 (pipes & redirection). Added `PROGRESS.md` visual
  tracker (119 exercises total). Slice 1: ex 1 ✅, ex 2 🔁 (stderr-bypasses-pipe, re-test
  cold), ex 3 ✅. Drilling attempt-first, answers verified in real bash.
