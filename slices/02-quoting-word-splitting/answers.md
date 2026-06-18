# Slice 2 — Answers

---

## Read exercises

**1.**
```bash
name="Alice"
echo 'Hello $name'
```
**Output:**
```
Hello $name
```
**Why:** Single quotes are fully literal — no expansion of any kind happens inside them. `$name` is printed as-is.

---

**2.**
```bash
name="Alice"
echo "Hello $name"
```
**Output:**
```
Hello Alice
```
**Why:** Double quotes allow `$var` expansion. The variable is substituted before `echo` runs.

---

**3.**
```bash
x="hello  world"
echo $x
echo "---"
echo "$x"
```
**Output:**
```
hello world
---
hello  world
```
**Why:** Unquoted `$x` is word-split by the shell on whitespace, then the resulting tokens are passed to `echo` as separate arguments. `echo` joins them with a single space, so the double space collapses. Quoted `"$x"` is passed as one argument with the internal spacing intact.

---

**4.**
```bash
file="my report.txt"
wc -w $file
```
**Output:**
```
wc: my: No such file or directory
wc: report.txt: No such file or directory
0 total
```
**Why:** Unquoted `$file` is word-split on the space, so the shell passes `wc` two arguments: `my` and `report.txt`. Neither file exists. The fix is `wc -w "$file"`. This is the canonical spaces-in-filename bug — it also explains why `rm $file` is dangerous.

---

**5.**
```bash
x="a b c"
[ -z $x ] && echo "empty" || echo "not empty"
```
**Output:**
```
bash: [: too many arguments
not empty
```
**Why:** Unquoted `$x` word-splits to three tokens: `a`, `b`, `c`. The `[` command sees `[ -z a b c ]` — 4 arguments — and errors with `too many arguments` (exit code 2). The `||` branch then runs. (A *two*-word value like `x="a b"` instead gives `[: a: binary operator expected` — different word count, different error.) Fix: always quote: `[ -z "$x" ]`.

---

**6.**
```bash
show_args() {
  echo "count: $#"
  for a in $@; do echo "  [$a]"; done
}
show_args "hello world" foo
```
**Output:**
```
count: 2
  [hello]
  [world]
  [foo]
```
**Why:** `$#` correctly shows 2 (the shell counted before calling the function). But unquoted `$@` is word-split inside the loop, breaking `"hello world"` into two separate words. With `"$@"` the output would be:
```
count: 2
  [hello world]
  [foo]
```
`"$@"` is the only form that preserves each original argument exactly.

---

**7.**
```bash
IFS=:
x="a:b:c"
for w in $x; do echo "word: $w"; done
```
**Output:**
```
word: a
word: b
word: c
```
**Why:** `IFS` controls which characters trigger word-splitting. Setting it to `:` makes the shell split `a:b:c` on colons. Quoting `"$x"` would suppress splitting and the loop would iterate once with `a:b:c` intact.

---

**8.**
```bash
echo *.xyz
```
**Output (no matching files present):**
```
*.xyz
```
**Why:** By default bash leaves an unmatched glob pattern as a literal string. It does NOT expand to empty and does NOT error. This trips up scripts that assume a failed glob yields nothing — they silently operate on the literal `*.xyz` string instead. Enable `nullglob` (`shopt -s nullglob`) to get empty expansion instead.

---

## Write exercises

**9.** Safe `wc -l` with a filename that may contain spaces:
```bash
wc -l "$file"
```
Always quote the variable. Test with `file="my report.txt"` and a file by that name. Edge case: if `$file` is unset, `"$file"` expands to `""` and `wc -l ""` errors cleanly rather than silently doing nothing.

---

**10.** Pass all positional args through to `grep`:
```bash
grep "$@"
```
`"$@"` is the only correct form — it expands each argument as a separate quoted word, so arguments with spaces survive intact. Test: call your wrapper as `wrapper "search term" myfile.txt` and verify grep receives exactly two arguments.
