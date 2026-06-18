# Slice 7 — Answers

---

## 1. Variable assignment — spaces matter

**What it prints:**
```
Hello, Alice
```

**If you change `name=Alice` to `name = Alice`:**
```
bash: line 2: name: command not found
Hello, 
```

**Why:** Bash parses `name = Alice` as: run a command called `name` with two arguments (`=` and `Alice`). The assignment never happens, so `$name` expands to the empty string. The error goes to stderr; `echo` still runs and prints `Hello, ` (with a trailing space from the empty expansion).

---

## 2. `"$*"` vs `"$@"` — the word-boundary trap

**Called as:** `script.sh "hello world" "foo" "bar"`

**Real output:**
```
--- using $*
  arg: hello world foo bar
--- using $@
  arg: hello world
  arg: foo
  arg: bar
```

**Why:** `"$*"` joins all positional args into one single string (separated by the first char of `$IFS`, a space by default). One iteration, one big blob. `"$@"` preserves each original argument as its own word. When filenames have spaces, `"$*"` is almost always wrong.

---

## 3. Parameter expansion on a filename

Variable: `f="archive.tar.gz"` (14 characters)

**Real output:**
```
14
tar.gz
gz
archive.tar
archive
```

**Line by line:**
- `${#f}` → `14` — character count of the string
- `${f#*.}` → `tar.gz` — strip shortest match of `*.` from front (strips `archive.`)
- `${f##*.}` → `gz` — strip longest match of `*.` from front (strips `archive.tar.`)
- `${f%.*}` → `archive.tar` — strip shortest match of `.*` from end (strips `.gz`)
- `${f%%.*}` → `archive` — strip longest match of `.*` from end (strips `.tar.gz`)

**Test tip:** Change `f` to `"plain"` (no dots) and rerun — all stripping expansions fall back to the original string unchanged.

---

## 4. `read` vs `read -r` — backslash eating

**Real output:**
```
foobar
foo\bar
```

**Without `-r`:** `read` treats `\b` as an escape sequence — the backslash is consumed, leaving `foobar`. This silently corrupts data containing backslashes (Windows paths, regex patterns, etc.).

**With `-r`:** `read -r` takes the input literally. `foo\bar` is stored as-is.

**Rule of thumb:** Always use `read -r` unless you specifically need the legacy escape-processing behaviour (you almost never do).

---

## 5. `local` — function variable scope

**Real output:**
```
inside bad_fn: x=99
after bad_fn: x=99
inside good_fn: x=99
after good_fn: x=10
```

**The bug:** `bad_fn` sets `x=99` without `local`, which modifies the global `x`. After `bad_fn` returns, the outer `x` is permanently changed to `99`.

**The fix:** Add `local x=99` inside `bad_fn` (as `good_fn` already does). `local` confines the variable to the function's scope; the outer `x=10` is unaffected.

---

## 6. `return` only carries an integer status

**Real output:**
```
ex_return.sh: line 5: return: Alice: numeric argument required
exit status: 2
```

**Why:** `return` sets the function's exit status — an integer in the range 0–255. You cannot use it to pass a string back to the caller.

**The correct pattern** to "return" a string:
```bash
get_name() {
  echo "Alice"
}
name=$(get_name)   # captures stdout
echo "$name"       # → Alice
```

---

## 7. `shift` and positional params

**Called as:** `script.sh alpha beta gamma delta`

**Real output:**
```
Script: ex_shift.sh
First: alpha
After shift, first is now: beta
Remaining count: 3
All remaining: beta gamma delta
```

**What `shift` does:** Discards `$1` and renumbers: old `$2` → new `$1`, old `$3` → new `$2`, and so on. `$#` decrements by 1.

**`shift 2`** would drop both `$1` and `$2` in one step, so `$1` would become `gamma`, `$#` would be `2`, and `$@` would be `gamma delta`.

**Common pattern:** `shift` inside a `while [[ $# -gt 0 ]]` loop is a standard way to consume arguments one at a time.

---

## 8. Real `script.sh` — what it does and where's the bug

**The script:**
```bash
#!/usr/bin/env bash

read foo

echo "you said $foo"
el diablo loco
```

**What it does:** Reads one line from stdin into `$foo`, then echoes it back. The `#!/usr/bin/env bash` shebang tells the kernel to run this file with whatever `bash` is first on `$PATH` — portable across systems where bash may not live at `/bin/bash`.

**Running it:**
```
echo "hello" | bash script.sh
```

**Real output:**
```
you said hello
script.sh: line 6: el: command not found
```
Exit status: `127`

**The bug:** Line 6 — `el diablo loco` is a stray line of text that bash tries to execute as a command. `el` is not a command, so bash errors with exit code 127 (command not found). Everything before it still runs, so you do see `you said hello` first — but the script exits non-zero, which would cause it to be aborted if `set -e` were active.

**Fix:** Delete line 6.

**How to test:** Run with `echo "hello" | bash script.sh` and check `echo $?` — you should see `127`. After deleting the line, `echo "hello" | bash script.sh` should print `you said hello` with exit status `0`.

---

## 9. Function with `local`

```bash
#!/usr/bin/env bash

greet() {
  local name=$1
  echo "Hello, ${name}!"
}

greet "World"
```

**Output:**
```
Hello, World!
```

**Why `local name=$1` matters:** Without `local`, `name` would be global. If the caller already had a variable called `name`, this function would silently overwrite it. `local` confines the variable to this function's scope.

**Test:** Add `name="outer"` before calling `greet "World"`, then `echo "$name"` after — it should still print `outer`.

---

## 10. `while read -r` loop over a file

```bash
#!/usr/bin/env bash

while read -r line; do
  echo "shell: $line"
done < /etc/shells
```

**Why `< /etc/shells` instead of `cat /etc/shells | while`:** The pipe form runs the `while` loop in a subshell. Any variables you set inside the loop are lost when the subshell exits. Redirecting the file directly into the loop keeps everything in the current shell.

**Test:** Add a counter variable inside the loop and print it after — it works with `<` redirection, fails to increment with the pipe form.

---

## 11. Capstone — `linecount.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 FILE [FILE...]" >&2
  exit 1
}

[[ $# -eq 0 ]] && usage

for file in "$@"; do
  if [[ ! -f "$file" ]]; then
    echo "ERROR: not a file: $file" >&2
    continue
  fi
  count=$(wc -l < "$file")
  echo "$count $file"
done
```

**Verified output — normal run:**
```
3 /tmp/test1.txt
2 /tmp/my test file.txt
```

**Verified output — with a missing file:**
```
3 /tmp/test1.txt
ERROR: not a file: /tmp/nonexistent.txt
```
Exit status: `0` (the `continue` keeps processing remaining files).

**Key decisions:**
- `"$@"` in the `for` loop: preserves filenames with spaces as single tokens.
- `wc -l < "$file"` rather than `wc -l "$file"`: the `<` redirect makes `wc` read from stdin, so output is just the number without the filename appended.
- `continue` instead of `exit` on bad input: reports the error and moves on to the next argument rather than bailing on everything.
- `set -euo pipefail`: any unexpected error (e.g. a subshell failing) aborts immediately.

**How to test robustly:**
1. Call with no args — should print usage to stderr and exit 1.
2. Call with a file whose name contains spaces — count should be correct.
3. Call with a directory instead of a file — should print `ERROR:` and continue.
4. Call with a mix of valid and invalid args — valid ones should still print.
