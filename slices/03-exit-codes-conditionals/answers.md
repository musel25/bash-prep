# Slice 3 — Answers

---

### 1.

```
ls exit=2
echo exit=0
```

**Why:** `ls /nonexistent` exits 2 (file not found). The first `echo` prints that, but *also sets `$?` to 0* because `echo` itself succeeds. The second `echo` captures that new `$?`. Every command — including `echo` — overwrites `$?`. Capture it immediately: `rc=$?`.

Real output:
```
ls exit=2
echo exit=0
```
Exit code at end: `0`

---

### 2.

```
yes
```

`echo "never"` does NOT print. The chain short-circuits at `false`: `true` exits 0, `echo "yes"` runs and exits 0, `false` exits 1 — `&&` stops, the rest of the chain is skipped. `$?` is 1 because the last command that *ran* was `false`.

Real output:
```
yes
exit=1
```

---

### 3.

```
fallback
exit=0
```

**Why:** `false` exits 1, so `||` runs `echo "fallback"`, which exits 0. That 0 becomes `$?`.

---

### 4.

```
ROLLBACK
exit=0
```

**The trap:** `deploy` succeeds (exit 0), so `&&` runs `verify`. `verify` fails (exit 1). Now `||` sees the non-zero exit of `verify` — not of `deploy` — and runs `echo "ROLLBACK"`. The ROLLBACK branch fires even though the deploy itself was fine. `$?` is 0 because `echo` succeeded.

This is why `a && b || c` is not a safe if/else: if `b` fails, `c` always runs.

---

### 5.

```bash
name="John Smith"
[ $name = "John Smith" ]
echo "exit=$?"
```

**Output:**
```
bash: [: too many arguments
exit=2
```

**Why:** Without quotes, `$name` word-splits into two tokens: `John` and `Smith`. `[ ]` sees `[ John Smith = "John Smith" ]` — three words on the left where it expects one — and errors. Always quote: `[ "$name" = "John Smith" ]`.

---

### 6.

```bash
name="John Smith"
[[ $name = "John Smith" ]]
echo "exit=$?"
```

**Output:**
```
exit=0
```

**Why:** `[[ ]]` is a bash keyword, not a command. It suppresses word-splitting on unquoted variables, so `$name` is treated as a single token regardless. No error, comparison succeeds.

---

### 7.

```
numeric: yes
string: no
```

**Why:**
- `[ 10 -gt 9 ]`: `-gt` is numeric comparison. 10 > 9 → true.
- `[ "10" \> "9" ]`: `>` in `[ ]` is lexicographic string comparison. `"10"` starts with `"1"`; `"9"` starts with `"9"`. ASCII `'1'` (0x31) < `'9'` (0x39), so `"10"` sorts *before* `"9"` → false.

Bonus trap: without the backslash, `>` in `[ ]` is a **redirection operator** — it would create a file named `9` in your current directory and the test would silently pass. Use `[[ ]]` with `>` unescaped to avoid this.

---

### 8.

```
script continues
exit=0
```

**Why:** `set -e` does **not** abort when the failing command is in an `if` condition (or on the left of `||`, or in a non-final pipeline stage). This is explicitly carved out in POSIX/bash: the whole point of `if cmd` is that you're handling the failure yourself. The script continues normally.

---

### 9.

```
before
```

Then the script exits immediately. `"after"` is never printed.

**Why:** `false` is a bare command at the top level with `set -e` active. It exits 1, which triggers the `set -e` abort. Exit code: `1`.

Real output:
```
before
```
Overall exit: `1`

---

### 10.

```
A exit=0
B exit=1
```

**Why:** Without `pipefail`, the pipeline exit code is the exit code of the **last** command (`true` → 0). With `pipefail`, bash tracks every stage; `false` exited 1, so the pipeline exit is 1 even though `true` succeeded at the end.

This is the standard gotcha: `grep "pattern" file | wc -l` — if `grep` finds nothing (exit 1), without `pipefail` your script sees exit 0 and thinks everything worked.

---

### 11.

```
default
exit=0
```

**Why:** `${MISSING:-"default"}` uses bash's default-value expansion. Even with `set -u`, the `:-` form **does not** trigger the unbound-variable error — it substitutes the default instead. This is the correct safe idiom. Without the `:-`, `set -u` would print an error and exit.

---

### 12.

```
true
```

**Why:** `[ 0 ]` tests whether the string `"0"` is non-empty. It is (it's one character), so the test is true. `[ ]` in single-argument form is equivalent to `[ -n "$arg" ]`. This trips up anyone coming from C, Python, or JavaScript where `0` is falsy. In shell `[ ]`, **every non-empty string is true**.

To test whether a number is zero: `[ "$n" -eq 0 ]`.

---

### 13.

```bash
make test || { echo "Tests failed, aborting"; exit 1; }
```

**Edge-case note:** The `{ …; }` group is needed because `||` only chains to a single command. Without braces, `exit 1` would be chained with `&&` after the echo, not inside the `||` branch.

---

### 14.

```bash
set -euo pipefail
```

Place this at the top of every non-trivial script, right after the shebang (`#!/usr/bin/env bash`).

- `-e`: abort on error
- `-u`: abort on unset variable
- `-o pipefail`: catch failures anywhere in a pipeline

**Edge-case note:** Know the `set -e` exceptions cold (if-conditions, `||` operands, non-final pipeline stages) — you'll be asked about them.

---

### 15.

**Bug:** If `send_alert "success"` fails (e.g., network error), then `||` fires `send_alert "failure"` even though the job succeeded. You end up sending a false failure alert.

**Fix:**

```bash
if run_job; then
  send_alert "success"
else
  send_alert "failure"
fi
```

`if/then/else/fi` is the only truly safe conditional in bash. The `a && b || c` pattern is fine when `b` cannot fail; it's a bug waiting to happen otherwise.
