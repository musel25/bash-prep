# Slice 1 — Answers

---

## Read exercises

### 1.
```bash
ls /nonexistent | wc -l
```
**Output (terminal):**
```
ls: cannot access '/nonexistent': No such file or directory
0
```
**Why:** `ls` writes the error to **stderr** (fd 2). The pipe connects only **stdout**
(fd 1). `wc -l` receives an empty stream and counts 0 lines. The error message bypasses
the pipe and goes straight to the terminal.

---

### 2.
```bash
ls /nonexistent 2>&1 | wc -l
```
**Output:**
```
1
```
**Why:** `2>&1` duplicates fd 2 onto fd 1 *before* the pipe is set up, so stderr is
merged into the same stream that the pipe carries. Now `wc -l` sees the one-line error
message and counts 1.

---

### 3.
```bash
{ echo "stdout"; echo "stderr" >&2; } 2>&1 >capture.txt
```
**Terminal shows:**
```
stderr
```
**`capture.txt` contains:**
```
stdout
```
**Why — the ordering trap:** Redirections are applied left-to-right.

1. `2>&1` — at this moment stdout still points at the terminal, so stderr is duped to
   the terminal.
2. `>capture.txt` — stdout is now redirected to the file, but fd 2 has already been
   snapshotted; it keeps pointing at the terminal.

Result: stdout goes to the file, stderr goes to the terminal — the **opposite** of what
most people expect.

The correct order to capture both: `{ ... } >capture.txt 2>&1`

How to test it: run both variants, `cat capture.txt`, and watch what hits the terminal.

---

### 4.
```bash
false | true
echo "exit: $?"
echo "PIPESTATUS: ${PIPESTATUS[@]}"
```
**Output:**
```
exit: 0
PIPESTATUS: 1 0
```
**Why:** `$?` is the exit code of the **last** command in the pipeline (`true` → 0).
`false` failed (exit 1) but its code is masked. `${PIPESTATUS[@]}` preserves per-command
codes: index 0 = `false` (1), index 1 = `true` (0).

**Danger:** In a script without `set -o pipefail`, `false | true` looks like success.
Silent data-loss pipelines (`generate | upload`) can fail invisibly.

Note: `${PIPESTATUS[@]}` must be captured **immediately** after the pipeline — the next
command overwrites it.

---

### 5.
```bash
set -o pipefail
grep NOMATCH /etc/hostname | wc -l
echo "exit: $?"
```
**Output:**
```
0
exit: 1
```
**Why:** `grep` finds no match → exits 1. Without `pipefail`, `$?` would be 0 (from
`wc`). With `pipefail`, the pipeline's exit code is the **rightmost non-zero** exit code
in the pipe. `wc -l` still receives the (empty) stdout stream and prints 0, but the
overall pipeline exit is 1.

---

### 6.
```bash
echo -e "a\nb\nc" | tee /tmp/out.txt | wc -l
```
**Terminal shows:**
```
3
```
**`/tmp/out.txt` contains:**
```
a
b
c
```
**Why:** `tee` writes its stdin to **both** the file and its own stdout simultaneously.
The downstream `wc -l` sees the three lines and counts 3. The file also gets all three
lines. Nothing is lost to either consumer.

---

## Write exercises

### 7. Save only stderr to `errors.log`

```bash
make build 2>errors.log
```
Stdout goes to the terminal; only fd 2 is redirected to the file.

How to test: `make build 2>errors.log; cat errors.log` — confirm warnings/errors appear
in the file but normal build output still hits the screen.

---

### 8. Discard both stdout and stderr, keep exit code

```bash
curl https://example.com &>/dev/null
echo "exit: $?"
```
`&>` is bash shorthand for `>file 2>&1`. Alternatively: `curl https://example.com
>/dev/null 2>&1`.

How to test: compare with a bad URL (`curl https://bad.invalid &>/dev/null; echo $?`) —
you should still see a non-zero exit code even though nothing printed.

---

### 9. Detect which pipeline stage failed

```bash
generate_data | transform | load
echo "per-stage exits: ${PIPESTATUS[@]}"
```
`${PIPESTATUS[0]}` = `generate_data`, `[1]` = `transform`, `[2]` = `load`.

Capture immediately: `statuses=("${PIPESTATUS[@]}")` before any other command resets it.

Alternative: add `set -o pipefail` at the top of the script to make the whole pipeline
fail fast if any stage fails (but you lose the granularity of *which* stage failed).
