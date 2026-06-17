# Plan — bash-prep

## Goal

Drilling Bash + Unix command-line fundamentals to pass technical screens — reach the point
where I can read a pipeline and know what it does, write a basic command without guessing,
and not get blindsided by the classic gotchas.

**Shape:** Teach → drill ladder. Each topic: Claude teaches the concept with real executed
output, then drills me, then I explain it back before we move on. Comprehension ("read &
reason") is the proving ground; fluency is the goal.

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
- [ ] **Slice 6 — Variables & a real script.** shebang, `$1`/`$@`, loops — tie it together
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
- No process substitution, traps, signals, or job control — past "pass a screen" for now.

## Open unknowns

- Target timeline / specific company screen format — unknown, not blocking. Revisit if a
  real deadline appears.

## Log

> Append-only. One line per session: date — what got proven.

- 2026-06-17 — Project mapped: goal + 6 slices + shape decided. No code yet.
