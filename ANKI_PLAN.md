# Anki deck plan — `Bash — Modal screen`

Spaced-repetition layer over `CHEATSHEET.md` + the `slices/` & `mock/` answer keys.
Goal: keep the reading-screen reflexes warm daily until the Modal FDE-ML screen (~2026-06-29).

## Shape

- **Deck:** `Bash — Modal screen` (created fresh via AnkiConnect; no prior bash deck).
- **Note type:** Basic (Front/Back) — default model, portable, no custom CSS needed.
  Commands wrapped in `<pre>` so they render monospaced.
- **Format:** mostly **reading drills** — Front shows a snippet and asks *"what does this
  print / do / where's the gotcha?"*; Back gives output + the *why* + the edge case. A
  minority are command/flag recall.
- **Tags:** one per slice so you can study a weak area in isolation —
  `pipes` `quoting` `exit-codes` `find-filter` `text` `perms-proc` `scripting` `mock`
  (plus `bash-prep` on every card).
- **Evidence rule:** every output-prediction card's answer is the **bash-verified** output
  from the answer keys (or freshly run in `bash -c`). No asserted-from-memory outputs.

## Distribution (~82 cards)

| Tag | Slice | Cards | Emphasis |
|-----|-------|-------|----------|
| `pipes` | 1 — pipes & redirection | 13 | streams, `2>&1` ordering, PIPESTATUS, `tee`, `&>` |
| `quoting` | 2 — quoting & word-splitting | 12 | `"$x"` vs `$x`, `"$@"` vs `"$*"`, globbing, `for f in $(ls)` |
| `exit-codes` | 3 — exit codes & conditionals | 13 | `$?`, `&&`/`||` not-if-else, `[ ]` vs `[[ ]]`, `set -euo pipefail` |
| `find-filter` | 4 — find & filter | 11 | grep flags, `.` in regex, sort/uniq adjacency, `-print0`/`xargs -0` |
| `text` | 5 — text processing | 10 | cut TAB/space trap, sed `s///g`, awk fields, `tail -n +2` |
| `perms-proc` | 6 — permissions/processes/concurrency | 13 | octal, dir x-bit, SIGTERM vs SIGKILL, `&`+`wait`, fork cost |
| `scripting` | 7 — variables & scripting | 10 | `name=` spacing, `local`, subshell scope, shebang, param expansion |

Cross-cutting mock-style snippets are tagged with their topic **and** `mock`.

## Build pipeline

1. `build_deck.py` holds all card data (front HTML, back HTML, tags).
2. Script verifies a sample of output-prediction snippets in `bash` at build time and
   aborts if any disagree with the stored answer.
3. `createDeck` then `addNotes` via AnkiConnect (`localhost:8765`). `allowDuplicate:false`
   so re-runs don't double-insert.
4. Report inserted / skipped counts.

## How to study

- New cards/day: ~15; reviews uncapped (deck is small, screen is close).
- When a card's snippet feels obvious, **say the answer out loud first**, then flip — the
  interview is verbal explain-back, not recognition.
- A card you only get after thinking "oh right" is a 🔁 — those are the ones that bite under
  pressure (mirrors `PROGRESS.md`).
