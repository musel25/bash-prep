# Progress — bash-prep

**Overall:** 19 / 97 drilled · **Slice 2 complete** ✅ (10/10)

```
Slice 1  ██████████████ 9/9    pipes & redirection   ✅ (re-test Read 4 cold)
Slice 2  ██████████████ 10/10  quoting & word-splitting   ✅
Slice 3  ·············· 0/15   exit codes & conditionals   ← here next
Slice 4  ·············· 0/11   find & filter
Slice 5  ·············· 0/13   text processing
Slice 6  ·············· 0/10   permissions, processes & concurrency
Slice 7  ·············· 0/11   variables & scripting
Mock     ·············· 0/18   Modal-style mixed bank
```

> Bank pruned 2026-06-18: cut 23 trivia/mechanics exercises (120 → 97), keeping the
> reading-screen-relevant gotchas + the full mock. Slices renumbered; see git history for
> what was removed.

## Legend

- ✅ nailed it first try
- 🔁 got it, but only after a correction → **revisit before the interview**
- ⬜ not yet attempted

The 🔁 column is the real signal: those are the gotchas that bit you once and will bite
again under pressure. A slice isn't "done" for interview purposes until its 🔁s are reviewed
and flipped to ✅ on a clean re-attempt.

---

## Slice 1 — Pipes & redirection  (Read 1–6, Write 7–9)

Read:  1 ✅   2 ✅   3 ✅   4 ✅   5 ✅   6 ✅
Write: 7 ✅   8 ✅   9 ✅

- ✅ **Write 7** (`make build 2>errors.log`) — after a detour: first tried `2>&1 | touch`,
  which merges channels (wrong direction) and `touch` discards piped data. Landed it.
- ✅ **Write 8** (`curl ... >/dev/null 2>&1`) — first try; understood exit code survives.
- ✅ **Write 9** (`${PIPESTATUS[@]}` on the next line) — right tool; corrected the "pipe it
  to the end" phrasing (PIPESTATUS is a variable, read it immediately, don't pipe into it).

- ✅ **Read 4** (pipeline exit code) — rebuilt from fundamentals; got `exit: 0`. Re-test
  cold: the `PIPESTATUS` line prints `0`, not `1 0`, because the preceding `echo` overwrites
  PIPESTATUS — must read it on the line *immediately* after the pipe.
- ✅ **Read 5** (`set -o pipefail`) — got `wc`=0 and `exit: 1`. Correction logged: it's
  **grep** that failed (exit 1, no match), not wc; pipefail surfaced it. PIPESTATUS = `1 0`.

- ✅ **Read 1** (`ls /nonexistent | wc -l`) — cleared on cold re-test. Core mechanism solid
  (stderr bypasses pipe → `wc -l` counts 0). One slip earlier: invented a phantom "1";
  nothing counts the error line — it never enters the pipe.
- ✅ **Read 2** (`2>&1 | wc -l`) — confirmed the contrast: `2>&1` routes the error into the
  pipe → counted → 1.
- ✅ **Read 3** (the `2>&1 >file` ordering trap) — got the conclusion (stderr→terminal,
  stdout→file). Tightened the *why*: `2>&1` snapshots fd1's current target first, then
  `>file` moves fd1; fd2 stays pinned to the terminal.

## Slice 2 — Quoting & word-splitting  (Read 1–8, Write 9–10)
Read:  1 ✅   2 ✅   3 ✅   4 ✅   5 ✅   6 ✅   7 ✅   8 ✅
Write: 9 ✅   10 ✅

- Read 8 bonus noted: zsh *errors* on an unmatched glob (`no matches found`) while bash
  leaves the literal pattern — concrete reason this project drills in bash, not zsh.
- ✅ **Write 9** — quoting was correct (`"$file"`), but first answer `echo "$file" | wc -l`
  counts the *filename string* (always 1), not the file. Fix: `wc -l "$file"`. read-vs-echo slip.

- ✅ **Read 5** (`[ -z $x ]`) — right output (`not empty`) but for the wrong reason: the
  unquoted split makes `[` crash with "too many arguments" (non-zero), so `||` fires. The
  logic never ran. Lesson: always quote vars in `[ ]` → `[ -z "$x" ]`.

## Slice 3 — Exit codes & conditionals  (Read 1–12, Write 13–15)
Read/Write: 1–15 ⬜

## Slice 4 — Find & filter  (Read 1–7, Write 8–11)
Read/Write: 1–11 ⬜

## Slice 5 — Text processing  (Read 1–10, Write 11–13)
Read/Write: 1–13 ⬜

## Slice 6 — Permissions, processes & concurrency  (Read 1–7, Write 8–10)
Read/Write: 1–10 ⬜

## Slice 7 — Variables & scripting  (Read 1–8, Write 9–11)
Read/Write: 1–11 ⬜

## Mock — Modal-style bank
1–18 ⬜
