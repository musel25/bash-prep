# Slice 3 — Exit codes & conditionals

## Quick intro (cheat-sheet)

| Syntax | What it does |
|---|---|
| `$?` | Exit code of the **last command** (0 = success, 1–255 = failure) |
| `true` | Does nothing, exits 0 |
| `false` | Does nothing, exits 1 |
| `cmd1 && cmd2` | Run `cmd2` only if `cmd1` exits 0 (short-circuit AND) |
| `cmd1 \|\| cmd2` | Run `cmd2` only if `cmd1` exits **non-zero** (short-circuit OR) |
| `if cmd; then…fi` | Branch on `cmd`'s **exit code**, not on any "boolean value" |
| `[ expr ]` / `test expr` | POSIX test; performs word-splitting; all vars should be quoted |
| `[[ expr ]]` | Bash keyword; no word-splitting; supports `&&`, `\|\|`, `<`, `>`, `=~` |
| `[ a -eq b ]` | Numeric equal (`-ne -lt -gt -le -ge` variants) |
| `[ a = b ]` | String equal (also `!=`; POSIX portable) |
| `[ a == b ]` | String equal (bash extension inside `[ ]`; prefer `=`) |
| `[[ a > b ]]` | String lexicographic greater-than (safe, no globbing) |
| `[[ str =~ regex ]]` | ERE regex match (bash `[[` only) |
| `[ -z "$s" ]` | True if string is empty |
| `[ -n "$s" ]` | True if string is non-empty |
| `[ -f path ]` | True if path exists and is a regular file |
| `[ -d path ]` | True if path exists and is a directory |
| `[ -e path ]` | True if path exists (any type) |
| `[ -x path ]` | True if path exists and is executable |
| `set -e` | Exit script on any command that returns non-zero (with exceptions) |
| `set -u` | Treat unset variables as errors |
| `set -o pipefail` | Pipeline exit = exit code of the **first** failing stage |
| `set -euo pipefail` | All three combined; the standard defensive idiom |

---

## Classic gotchas

- **`a && b \|\| c` is NOT if/else.** If `b` fails (exits non-zero), `c` runs — even though `a` succeeded. People write `deploy && verify \|\| rollback` expecting it to work like an if/else, but if `verify` fails the rollback fires correctly *for the wrong reason*, and `$?` ends up 0.

- **`set -e` has blind spots.** A failing command inside an `if` condition, on the left side of `\|\|`, or in any non-final pipeline stage **does not** trigger exit. This surprises everyone.

- **`[ 10 > 9 ]` is wrong for numbers.** Inside `[ ]`, `>` is a redirection operator (creates a file named `9`!). Use `-gt` for numbers. String comparison of `"10" > "9"` is false because `"1"` sorts before `"9"` lexicographically.

- **`$?` is overwritten by every command, including `echo`.** If you need the exit code, capture it immediately: `rc=$?` before you do anything else.

- **Unquoted variables in `[ ]` cause "too many arguments" or "binary operator expected".** `name="John Smith"` then `[ $name = "John" ]` → error. Always quote: `[ "$name" = "John" ]`. In `[[ ]]` this doesn't matter — word-splitting is suppressed.

---

## Exercises

Try each before peeking at answers.md.

### Read — what does this do / print? (and what is the exit code?)

**1.** What does `$?` equal after each of these two lines, and why?

```bash
ls /nonexistent > /dev/null 2>&1
echo "ls exit=$?"
echo "echo exit=$?"
```

---

**2.** What prints? What is `$?` at the end?

```bash
true && echo "yes" && false && echo "never"
echo "exit=$?"
```

---

**3.** What prints? What is `$?` at the end?

```bash
false || echo "fallback"
echo "exit=$?"
```

---

**4.** (The big trap.) What prints? What is `$?` at the end?

```bash
deploy()  { return 0; }   # deploy succeeds
verify()  { return 1; }   # verify fails

deploy && verify || echo "ROLLBACK"
echo "exit=$?"
```

---

**5.** What is the output and exit code?

```bash
name="John Smith"
[ $name = "John Smith" ]
echo "exit=$?"
```

---

**6.** Same intent, different bracket style. What is the output and exit code now?

```bash
name="John Smith"
[[ $name = "John Smith" ]]
echo "exit=$?"
```

---

**7.** Numeric vs string comparison. What do each of these print?

```bash
[ 10 -gt 9 ] && echo "numeric: yes" || echo "numeric: no"
[ "10" \> "9" ] && echo "string: yes" || echo "string: no"
```

---

**8.** `set -e` with an `if` condition. Does the script exit early?

```bash
set -e
if grep -q "NOMATCH" /etc/hostname; then
  echo "found"
fi
echo "script continues"
echo "exit=$?"
```

---

**9.** `set -e` with a bare failing command. What happens?

```bash
set -e
echo "before"
false
echo "after"
```

---

**10.** `set -o pipefail` — what does each print?

```bash
# without pipefail
false | true; echo "A exit=$?"

# with pipefail
set -o pipefail
false | true; echo "B exit=$?"
```

---

**11.** `set -u` — what happens?

```bash
set -u
echo ${MISSING:-"default"}
echo "exit=$?"
```

---

**12.** `[ 0 ]` — true or false?

```bash
if [ 0 ]; then
  echo "true"
else
  echo "false"
fi
```

---

### Write — how would you …?

**13.** Run `make test`; if it fails, print `"Tests failed, aborting"` and exit with code 1. Use only `&&`/`||`, no `if`.

**14.** Write a one-liner that checks whether `/etc/shadow` is readable by the current user and prints either `"readable"` or `"not readable"`. Use a file test.

**15.** Write the standard three-option safety header for a script that should abort on errors, treat unset variables as errors, and catch failures inside pipelines.

**16.** Write an `if` block that prints `"big"` if a variable `n` is numerically greater than 100, using `[ ]`. Why is `[ $n > 100 ]` wrong here?

**17.** A colleague writes:

```bash
run_job && send_alert "success" || send_alert "failure"
```

Explain the bug and rewrite it correctly using `if/then/else/fi`.

**18.** Capture the exit code of `curl https://example.com -o /dev/null -s` into a variable `rc`, then print `"ok"` or `"fail"` depending on it — without using `$?` a second time.
