# Slice 1 — Pipes & redirection

## Quick intro (cheat-sheet)

| Syntax | What it does |
|---|---|
| `cmd1 \| cmd2` | Connect cmd1's **stdout** to cmd2's **stdin** |
| `>file` | Redirect stdout to file, **truncating** it first |
| `>>file` | Redirect stdout to file, **appending** |
| `<file` | Feed file as **stdin** to command |
| `2>file` | Redirect **stderr** (fd 2) to file |
| `&>file` / `>&file` | Redirect **both** stdout and stderr to file (bash shorthand) |
| `2>&1` | Dup fd 2 to wherever fd 1 currently points |
| `1>/dev/null` / `>/dev/null` | Discard stdout |
| `2>/dev/null` | Discard stderr |
| `tee file` | Write stdin to **both** stdout and file simultaneously |
| `tee -a file` | Same as `tee` but **appends** to file |
| `${PIPESTATUS[@]}` | Array of exit codes for each command in the last pipeline |
| `set -o pipefail` | Pipeline fails if **any** command in it fails (not just the last) |

FD numbers to memorise: **0** = stdin, **1** = stdout, **2** = stderr.

---

## Classic gotchas

- **A pipe carries only stdout, not stderr.** `cmd | grep foo` will never match error
  messages — they bypass the pipe entirely and go straight to the terminal.

- **The ordering trap with `2>&1`.** Redirections are evaluated left-to-right.
  `cmd 2>&1 >file` means "dup stderr to wherever stdout points *right now* (terminal),
  *then* redirect stdout to file" — so stderr still goes to the terminal.
  The correct order is `cmd >file 2>&1`.

- **Pipeline exit status is the last command's exit code.** A failing command early in a
  pipe is silently swallowed. `false | true` exits 0. Use `${PIPESTATUS[@]}` or
  `set -o pipefail` to catch it.

- **`>file` truncates immediately**, before the command even runs. Running
  `sort file > file` wipes the file before `sort` reads it — you get an empty file.

- **`2>&1` is a *snapshot*, not a live link.** After `cmd >file 2>&1`, both fds point at
  the file. Changing stdout later doesn't move stderr along with it.

---

## Exercises

Try each before peeking at answers.md.

---

### Read — what does this do / print?

**1.**
```bash
echo "hello world" | wc -w
```
What does this print?

---

**2.**
```bash
ls /nonexistent | wc -l
```
What prints to the terminal and why? What does `wc -l` count?

---

**3.**
```bash
ls /nonexistent 2>&1 | wc -l
```
How is this different from exercise 2? What does `wc -l` count now?

---

**4.**
```bash
{ echo "stdout"; echo "stderr" >&2; } 2>&1 >capture.txt
```
After this runs, what is in `capture.txt`? What appears on the terminal?
*(This is the ordering-trap exercise — think carefully before answering.)*

---

**5.**
```bash
echo "first" > f.txt
echo "second" > f.txt
cat f.txt
```
What does `cat f.txt` print?

---

**6.**
```bash
false | true
echo "exit: $?"
echo "PIPESTATUS: ${PIPESTATUS[@]}"
```
What are the two values printed? Why might this be dangerous in a script?

---

**7.**
```bash
set -o pipefail
grep NOMATCH /etc/hostname | wc -l
echo "exit: $?"
```
What does `wc -l` print? What does `echo "exit: $?"` print? Why?

---

**8.**
```bash
echo -e "a\nb\nc" | tee /tmp/out.txt | wc -l
```
What prints to the terminal? What ends up in `/tmp/out.txt`?

---

### Write — how would you …?

**9.** Run `make build` and save **only stderr** to `errors.log`, letting stdout still
appear on the terminal.

**10.** Append the output of `date` to a file called `log.txt` without overwriting anything
already in it.

**11.** Run `curl https://example.com` and silently discard **both** stdout and stderr (you
only care about the exit code).

**12.** Find out whether any individual command in the pipeline
`generate_data | transform | load` failed, and which one.

**13.** Run `some_cmd` and have its output go to **both** the terminal and a file called
`run.log` at the same time.
