# bash-prep

Drilling Bash + Unix command-line fundamentals for the **Modal — Forward Deployed Engineer
(ML)** technical screen. The screen is a *reading* test: they show short snippets / command
lines and you talk through what they do, the edge cases, and how you'd test them — no AI in
the room. So this repo is a **pre-built exercise bank** you work through interactively.

Learning-first: the goal is understanding, not output. See [`PLAN.md`](./PLAN.md) for the
roadmap and [`CLAUDE.md`](./CLAUDE.md) for the learning contract.

## The exercise bank

Seven topic banks, ordered by interview payoff, then a mock round:

| # | Topic | Folder |
|---|-------|--------|
| 1 | Pipes & redirection | [`slices/01-pipes-redirection`](./slices/01-pipes-redirection) |
| 2 | Quoting & word-splitting | [`slices/02-quoting-word-splitting`](./slices/02-quoting-word-splitting) |
| 3 | Exit codes & conditionals | [`slices/03-exit-codes-conditionals`](./slices/03-exit-codes-conditionals) |
| 4 | Find & filter | [`slices/04-find-filter`](./slices/04-find-filter) |
| 5 | Text processing (cut/tr/sed/awk) | [`slices/05-text-processing`](./slices/05-text-processing) |
| 6 | Permissions, processes & concurrency | [`slices/06-permissions-processes`](./slices/06-permissions-processes) |
| 7 | Variables & a real script | [`slices/07-variables-scripting`](./slices/07-variables-scripting) |
| — | Mock round (mixed, Modal-style) | [`mock/`](./mock) |

Each topic folder has:
- **`README.md`** — a tight cheat-sheet intro (command → flag → what it does), the classic
  gotchas, then **exercises**: *read* ("what does this print?") and *write* ("how would you…?").
- **`answers.md`** — the answer key, with **real verified bash output** for every snippet.

## How to drill a topic

1. Read the cheat-sheet intro at the top of the folder's `README.md`.
2. Work the exercises — say the answer out loud / write it down **before** opening `answers.md`.
3. For *read* exercises, predict the exact output first, then check.
4. **Run things in real `bash`**, never the interactive `zsh` prompt — they word-split
   differently (that's literally Slice 2). Use `bash -c '…'` or `bash script.sh`.
5. When stuck or done, bring it back here — explain it back, and we move on only once it lands.

## Starting point

Comfortable with `cd`, `ls`, basic `grep`. Everything else — pipes, redirection, quoting,
exit codes, `find`, `awk`/`sed`, scripting, permissions — is new. Building from the ground up.
