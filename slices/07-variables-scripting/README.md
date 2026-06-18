# Slice 7 — Variables & a real script

## Quick intro (cheat-sheet)

| Syntax | What it does |
|---|---|
| `#!/usr/bin/env bash` | Shebang: finds `bash` on `$PATH` rather than hardcoding `/bin/bash` — safer across systems |
| `name=value` | Assign a variable — **no spaces** around `=` |
| `$name` / `${name}` | Expand a variable; `${name}` required when adjacent to other chars: `${name}s` |
| `$0` | Name of the script itself |
| `$1 $2 …` | Positional arguments passed to the script |
| `$#` | Number of positional arguments |
| `"$@"` | All positional args, each as a separate quoted word — **always use this in loops** |
| `"$*"` | All positional args as a **single** joined word (rarely what you want) |
| `shift` | Drop `$1`, shift remaining args down: `$2` becomes `$1`, etc. |
| `read -r var` | Read one line of stdin into `var`; `-r` stops backslash from being treated as escape |
| `while read -r line; do … done < file` | Iterate over every line of a file |
| `for x in …; do … done` | Word-by-word loop |
| `for ((i=0; i<n; i++)); do … done` | C-style arithmetic loop |
| `while cond; do … done` | Loop while condition is true |
| `until cond; do … done` | Loop until condition is true (opposite of while) |
| `$(( expr ))` | Arithmetic expansion — returns the result as a string |
| `(( expr ))` | Arithmetic evaluation — used as a condition (0 = true); can do `((i++))` |
| `${var:-default}` | Expand `$var`; if unset or empty, use `default` (does not assign) |
| `${var:=default}` | Expand `$var`; if unset or empty, **assign** `default` and expand it |
| `${#var}` | Length of `$var` in characters |
| `${var#prefix}` | Strip shortest matching `prefix` from the **front** |
| `${var##prefix}` | Strip longest matching `prefix` from the front |
| `${var%suffix}` | Strip shortest matching `suffix` from the **end** |
| `${var%%suffix}` | Strip longest matching `suffix` from the end |
| `f() { …; }` | Declare a function |
| `local x=val` | Variable scoped to the current function — **always use inside functions** |
| `return N` | Exit a function with status N (0–255, integers only) |
| `echo value` | The idiomatic way to "return" a string from a function (capture with `$(f)`) |
| `exit N` | Exit the entire script with status N |
| `set -e` | Exit immediately if any command fails |
| `set -u` | Treat unset variables as errors |
| `set -o pipefail` | Propagate failure from any command in a pipeline, not just the last |
| `set -euo pipefail` | All three together — standard header for robust scripts |

---

## Classic gotchas

- **Spaces around `=` break assignment.** `name = "Alice"` tries to run a command called `name` with arguments `=` and `Alice`. Bash reports `name: command not found`.

- **`"$*"` collapses all args into one word.** If `$1="hello world"` and `$2="foo"`, looping over `"$*"` gives a single iteration with the string `hello world foo`. Use `"$@"` to preserve word boundaries.

- **Unquoted `$@` splits on spaces.** `for f in $@` (no quotes) will word-split `"my file.txt"` into two tokens. Always write `for f in "$@"`.

- **`read` (without `-r`) eats backslashes.** `printf 'foo\\bar\n' | read line` stores `foobar` — the `\b` is treated as an escape. `read -r` disables that: stores `foo\bar`.

- **`return` only carries an integer status (0–255).** `return "Alice"` is an error. To "return" a string from a function, `echo` it and capture with `result=$(my_fn)`.

- **Integer arithmetic always truncates toward zero.** `$(( 7 / 2 ))` is `3`, not `3.5`. Bash has no floating-point arithmetic.

---

## Exercises

Try each before peeking at answers.md.

### Read — what does this do / where's the bug?

**1.** What does the following print? What happens if you change `name=Alice` to `name = Alice`?

```bash
#!/usr/bin/env bash
name=Alice
echo "Hello, $name"
```

---

**2.** What does this print? Why do the two loops produce different output?

```bash
#!/usr/bin/env bash
# called as: script.sh "hello world" "foo" "bar"
echo "--- using \$*"
for arg in "$*"; do
  echo "  arg: $arg"
done
echo "--- using \$@"
for arg in "$@"; do
  echo "  arg: $arg"
done
```

---

**3.** What does each line print? No bug here — just make sure you can predict all five outputs before running.

```bash
f="archive.tar.gz"
echo ${#f}
echo ${f#*.}
echo ${f##*.}
echo ${f%.*}
echo ${f%%.*}
```

---

**4.** What does this print? What is the gotcha with `read` (no `-r`)?

```bash
printf 'foo\\bar\n' | read line
echo "$line"

printf 'foo\\bar\n' | read -r line
echo "$line"
```

---

**5.** What does this print? Where's the bug — and what one-line fix addresses it?

```bash
#!/usr/bin/env bash
x=10

bad_fn() {
  x=99
  echo "inside bad_fn: x=$x"
}

good_fn() {
  local x=99
  echo "inside good_fn: x=$x"
}

bad_fn
echo "after bad_fn: x=$x"

x=10
good_fn
echo "after good_fn: x=$x"
```

---

**6.** What does this print? What's wrong with calling `return "Alice"` to "return" a string from a function?

```bash
#!/usr/bin/env bash
get_name() {
  return "Alice"
}
get_name
echo "exit status: $?"
```

---

**7.** What does this script do, what does it print when run as `script.sh alpha beta gamma delta`, and what would `shift 2` do instead?

```bash
#!/usr/bin/env bash
echo "Script: $0"
echo "First: $1"
shift
echo "After shift, first is now: $1"
echo "Remaining count: $#"
echo "All remaining: $@"
```

---

**8.** Read this real script (`script.sh` from this repo). What does it do? What is the bug, and what does the error look like at runtime?

```bash
#!/usr/bin/env bash

read foo

echo "you said $foo"
el diablo loco
```

Run it as: `echo "hello" | bash script.sh`

---

### Write — how would you …?

**9.** Write a one-liner that prints the length of the string stored in `$word`, then strips everything from the first `.` to the end (i.e. get just the base name before the first dot) — using only parameter expansion, no external commands.

---

**10.** Write a function `greet` that takes one argument (a name) and prints `Hello, <name>!`. Use `local` correctly. Call it with `greet "World"`.

---

**11.** Write a `while read -r` loop that reads `/etc/shells` line by line and prints each line prefixed with `shell:`. (Redirect the file into the loop, do not use `cat | while`.)

---

**12.** Write a C-style `for` loop that prints the squares of 1 through 5 using `$(( ))`.

---

**13. (Capstone)** Write a script `linecount.sh` that:
- Takes one or more file arguments (`$@`)
- Prints `<count> <filename>` for each file
- Skips (with an error message to stderr) any argument that is not a regular file
- Handles filenames with spaces correctly
- Starts with `set -euo pipefail`
- Prints a usage message to stderr and exits 1 if called with no arguments

Test it with a file whose name contains a space.
