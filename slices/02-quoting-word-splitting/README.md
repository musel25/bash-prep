# Slice 2 — Quoting & word-splitting

## Quick intro (cheat-sheet)

| Syntax | What it does |
|---|---|
| `'literal'` | Single quotes — everything inside is literal; no `$`, no `$()`, no `\` escapes |
| `"$var"` | Double quotes — expands `$var`, `$()`, `\`\`` but preserves spaces as one token |
| `$var` (unquoted) | Shell performs **word-splitting** (splits on IFS) then **globbing** on the result |
| `$(command)` | Command substitution — runs `command`, substitutes its stdout |
| `` `command` `` | Same as `$()` but harder to nest and read; prefer `$()` |
| `*` | Glob: matches any string of characters in filenames |
| `?` | Glob: matches exactly one character |
| `[abc]` | Glob: matches one character from the set |
| `"$@"` | All positional args, each as a **separate quoted word** — the safe form |
| `$@` (unquoted) | All positional args, then word-split — **breaks args that contain spaces** |
| `"$*"` | All args joined into **one word** using the first character of `IFS` as separator |
| `IFS` | Internal Field Separator — default is space, tab, newline; controls word-splitting |

**Rule of thumb:** quote every variable (`"$var"`) unless you deliberately want splitting or globbing.

---

## Classic gotchas

- **Unquoted variable with spaces becomes multiple arguments.** `rm $file` where `file="my report.txt"` runs `rm my report.txt` — two arguments, neither the intended file.
- **Glob no-match is not an error by default.** `echo *.xyz` with no matching files prints the literal string `*.xyz`, not an empty string. Scripts that assume an empty result silently do the wrong thing.
- **`[ -z $x ]` breaks when `$x` contains spaces.** The unquoted `$x` word-splits inside `[`, giving `[` too many arguments and a syntax error. Always write `[ -z "$x" ]`.
- **`$*` vs `"$@"` when args have spaces.** `$*` and unquoted `$@` both re-split on IFS, destroying args that contain spaces. Only `"$@"` preserves each original argument.
- **Unquoted substitution collapses whitespace.** `echo $x` where `x="hello  world"` prints `hello world` — the double space is gone. `echo "$x"` preserves it.

---

## Exercises

Try each before peeking at answers.md.

### Read — what does this do / print?

**1.**
```bash
name="Alice"
echo 'Hello $name'
```
What does this print?

---

**2.**
```bash
name="Alice"
echo "Hello $name"
```
What does this print?

---

**3.**
```bash
x="hello  world"
echo $x
echo "---"
echo "$x"
```
What are the three lines of output? Why do they differ?

---

**4.**
```bash
file="my report.txt"
wc -w $file
```
Assume the file `my report.txt` exists. What does this command actually do, and what error do you expect?

---

**5.**
```bash
x="a b c"
[ -z $x ] && echo "empty" || echo "not empty"
```
Does this print `empty`, `not empty`, or something else?

---

**6.**
```bash
show_args() {
  echo "count: $#"
  for a in $@; do echo "  [$a]"; done
}
show_args "hello world" foo
```
What does this print? What would change if you wrote `"$@"` instead?

---

**7.**
```bash
IFS=:
x="a:b:c"
for w in $x; do echo "word: $w"; done
```
What does this print?

---

**8.**
```bash
echo *.xyz
```
Run in a directory with no `.xyz` files. What prints?

---

### Write — how would you …?

**9.** You have a variable `file` that might contain spaces (e.g. `"my report.txt"`). Write the `wc -l` command that handles this safely.

**10.** Pass all positional arguments of a wrapper script through to `grep`, preserving any arguments that contain spaces.
