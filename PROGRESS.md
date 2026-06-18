# Progress — bash-prep

**Overall:** 3 / 97 drilled · **Slice 1 in progress** (3/9)

```
Slice 1  █████········· 3/9    pipes & redirection   ← here
Slice 2  ·············· 0/10   quoting & word-splitting
Slice 3  ·············· 0/15   exit codes & conditionals
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

Read:  1 ✅   2 ✅   3 ✅   4 ⬜   5 ⬜   6 ⬜
Write: 7 ⬜   8 ⬜   9 ⬜

- ✅ **Read 1** (`ls /nonexistent | wc -l`) — cleared on cold re-test. Core mechanism solid
  (stderr bypasses pipe → `wc -l` counts 0). One slip earlier: invented a phantom "1";
  nothing counts the error line — it never enters the pipe.
- ✅ **Read 2** (`2>&1 | wc -l`) — confirmed the contrast: `2>&1` routes the error into the
  pipe → counted → 1.
- ✅ **Read 3** (the `2>&1 >file` ordering trap) — got the conclusion (stderr→terminal,
  stdout→file). Tightened the *why*: `2>&1` snapshots fd1's current target first, then
  `>file` moves fd1; fd2 stays pinned to the terminal.

## Slice 2 — Quoting & word-splitting  (Read 1–8, Write 9–10)
Read/Write: 1–10 ⬜

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
