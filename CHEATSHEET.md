# Bash / Unix cheat-sheet — Modal reading screen

> Improved from the ChatGPT draft: inaccuracies fixed, the classic **gotchas** you drilled
> folded in, and the **concurrency/perf intuition** Modal named added. Mental model first,
> then commands, then the traps that actually get asked.
>
> Companion to the `slices/` exercise bank. Every "what does this print" claim here is
> verified in real **bash** (not zsh — they word-split differently).

---

## 0. Mental model

A command is `command options arguments`. Bash is mostly:

```
take input  →  transform / filter it  →  send output somewhere
```

Three streams on every process:

| fd | name   | default | redirect |
|----|--------|---------|----------|
| 0  | stdin  | keyboard | `< file` |
| 1  | stdout | terminal | `> file`, `>> file` |
| 2  | stderr | terminal | `2> file` |

**A pipe `|` connects stdout (fd 1) only.** stderr bypasses it. This single fact drives
half the gotchas below.

---

## 1. Navigation & viewing (the easy stuff)

```bash
pwd                 # where am I
ls -lah             # long, all (incl. hidden), human sizes
cd -                # previous directory   (~ = home, .. = up, / = root)
cat f               # dump small file
less f              # page big file: Space/b page, /word search, q quit
head -n 20 f        # first 20 lines
tail -n 20 f        # last 20 lines
tail -f app.log     # FOLLOW: stream new lines as they're appended (logs)
```

`tail -n +2 f` = **start at line 2** (skip header). `tail -n 2 f` = **last 2 lines**.
Opposite operations — confusing them silently corrupts pipelines.

---

## 2. Files & dirs

```bash
touch f             # create empty / bump mtime
mkdir -p a/b/c      # -p: make parents, no error if exists
cp -r src dst       # -r needed for directories
mv a b              # move OR rename (same op)
rm -rf dir          # -r recursive, -f force-no-prompt — no undo
```

---

## 3. Pipes & redirection — highest-frequency topic

```bash
cmd1 | cmd2         # cmd1 stdout → cmd2 stdin
echo hi > f         # overwrite (truncate) stdout to file
echo hi >> f        # append
sort < f            # file → stdin
cmd 2> err.log      # stderr only → file
cmd > out 2>&1      # stdout → file, THEN stderr → same place   ✅
cmd &> /dev/null    # bash shorthand for > /dev/null 2>&1 (discard both)
cmd | tee f         # write stdin to f AND pass it downstream
```

### GOTCHA — the `2>&1` ordering trap (gets asked constantly)

Redirections apply **left to right**, and `2>&1` copies *wherever fd 1 points right now*.

```bash
cmd 2>&1 > out.txt   # WRONG: stderr→terminal (fd1 still terminal), stdout→file
cmd > out.txt 2>&1   # RIGHT: stdout→file, then stderr→file
```

Mnemonic: **redirect stdout first, then point stderr at it.**

### GOTCHA — stderr bypasses the pipe

```bash
ls /nope | wc -l        # → 0   (error went to terminal, not into the pipe)
ls /nope 2>&1 | wc -l   # → 1   (2>&1 merges stderr into the piped stream)
```

---

## 4. Exit codes & conditionals

```bash
echo $?             # exit code of LAST command (0 = success, non-0 = fail)
rc=$?               # capture IMMEDIATELY — every command (even echo) overwrites $?
a && b              # run b only if a succeeded (exit 0)
a || b              # run b only if a failed
```

| code | meaning |
|------|---------|
| 0    | success |
| 1    | generic failure (grep: no match) |
| 2    | misuse / `[ ]` syntax error |
| 126  | found but not executable |
| 127  | command not found |
| 130  | killed by Ctrl+C (SIGINT, 128+2) |

### GOTCHA — `$?` and `PIPESTATUS` in a pipeline

`$?` is **only the last** stage. Per-stage codes live in `${PIPESTATUS[@]}`:

```bash
false | true
echo $?                  # → 0   (true's code; false's failure is masked)
echo "${PIPESTATUS[@]}"  # → 1 0 (read it on the VERY NEXT line; next cmd resets it)
```

### GOTCHA — `a && b || c` is NOT if/else

If `b` fails, `c` runs even though `a` succeeded:

```bash
deploy && verify || rollback   # rollback fires if VERIFY fails, not just deploy
```

The only safe conditional:

```bash
if deploy; then verify; else rollback; fi
```

### `[ ]` vs `[[ ]]`

- `[ ]` is a **command** (`test`) — unquoted vars word-split → `[: too many arguments`.
- `[[ ]]` is a **bash keyword** — suppresses word-splitting & globbing; `<` `>` work safely.
- Numeric vs string: `-eq -ne -lt -gt` are numeric; `=` `!=` `<` `>` are string (lexical).

```bash
[ 10 -gt 9 ]      # true  (numeric)
[ "10" \> "9" ]   # FALSE (lexical: '1' < '9'); and unescaped > would REDIRECT to file "9"
[ 0 ]             # true! single-arg [ ] tests non-EMPTY string; "0" is non-empty
```

### `set -euo pipefail` — top of every real script

- `-e` abort on any unchecked non-zero exit
- `-u` abort on unset variable
- `-o pipefail` pipeline fails if **any** stage fails (not just the last)

`set -e` **exemptions** (know these cold — common interview follow-up): commands in an
`if`/`while`/`until` condition, operands of `&&` `||` `!`, and non-final pipeline stages
are all shielded. `${VAR:-default}` also dodges `-u`.

---

## 5. Search — grep & find

```bash
grep -i pat f          # case-insensitive
grep -n pat f          # show line numbers
grep -r pat .          # recurse a tree
grep -ril pat . --include="*.py"   # recurse, ignore-case, list filenames, only .py
grep -c pat f          # COUNT matching lines (prefer over | wc -l, see gotcha)
grep -o pat f          # print only the matched part, one per line
grep -E 'a+'           # extended regex (+ ? | () without backslashes)
grep -F 'c.t'          # fixed string: . is literal, not "any char"
```

```bash
find . -name "*.py"            # by name (quote the glob so the shell doesn't expand it)
find . -type f -mtime -7 -size +10M   # files, modified <7 days, >10 MB
find . -name "*.log" -delete   # atomic per-file delete (safest for destructive ops)
```

`find` size units: `c` bytes, `k` kB, `M` MB, `G` GB. `-mtime -7` = within 7 days,
`+7` = older than 7 days.

### GOTCHA — `.` in regex, and `grep -c` vs `| wc -l`

```bash
grep "c.t" f     # . = ANY char → matches cat, cot, c.t, cbt...  use grep -F for literal
```

```bash
grep -c pat /nope        # exits 2, error surfaces           ✅ correct
grep pat /nope | wc -l   # prints 0, exit 0 — the pipe SWALLOWS grep's error  ⚠️
```

`grep -c` (and plain `grep`) exit **1 when zero matches** — under `set -e`, guard with
`|| true` when "no match" is a valid outcome.

### GOTCHA — `find | xargs` splits on whitespace

```bash
find . -name "*.log" | xargs wc -l            # "my app.log" → "my" + "app.log"  ⚠️
find . -name "*.log" -print0 | xargs -0 wc -l # null-delimited, space-safe       ✅
find . -name "*.log" -exec wc -l {} +         # also safe; + batches into one call
```

`-exec … {} \;` runs the command **once per file** (1 fork each). `-exec … {} +` and
`xargs` batch **many files per call** — much faster at scale.

---

## 6. Text processing — cut / sort / uniq / tr / sed / awk

```bash
wc -l f                # count lines  (-w words, -c bytes)
sort f                 # LEXICAL by default: 10 before 2
sort -n f              # numeric        (-r reverse, -h human sizes, -k2 by col 2)
uniq f                 # collapse ADJACENT dup lines only
uniq -c f              # prefix each group with its count
cut -d, -f1 f          # field 1, comma-delimited  (default delim is TAB, not space!)
tr -d '0-9'            # delete chars; tr 'a-z' 'A-Z' translates
```

### The top-N idiom (memorize)

```bash
sort f | uniq -c | sort -nr | head    # group, count, rank by frequency
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head   # top IPs
```

`uniq` only collapses **adjacent** lines → the leading `sort` is mandatory.

### sed / awk — enough to read

```bash
sed 's/old/new/'  f    # replace FIRST match per line
sed 's/old/new/g' f    # global (all matches per line)
sed -n '3,5p'     f    # print only lines 3–5 (-n suppresses default print)
awk '{print $1}'  f    # field 1 (whitespace-split; collapses runs of spaces)
awk -F, '{print $2}' f # comma as field separator
awk '$3 > 70'     f    # print rows where field 3 > 70
awk -F, '{s+=$2} END{print s}' f   # sum column 2
```

### GOTCHA — `cut -d' '` vs `awk` on padded columns

```bash
echo "alice   90" | cut -d' ' -f2    # → "" (cut splits on ONE space; field 2 is empty)
echo "alice   90" | awk '{print $2}' # → 90 (awk default FS = runs of whitespace)
```

`cut` also prints the **whole line** when the delimiter is absent (silent failure). `sed 'Np'`
without `-n` prints line N **twice** (default print + explicit `p`).

---

## 7. Permissions — Modal named this

`ls -l` first column: `-rwxr-xr--` = `[type][owner][group][other]`.

```
- rwx r-x r--
│  │   │   └ other: r--   read only
│  │   └──── group: r-x   read + execute
│  └──────── owner: rwx   read + write + execute
└─────────── type: -=file  d=dir  l=symlink
```

Octal: `r=4 w=2 x=1`, summed per class. `755`=rwxr-xr-x, `644`=rw-r--r--, `751`=rwx--x--x.

```bash
chmod +x s.sh          # add execute (may leave umask write bits — 755 is explicit)
chmod 755 deploy.sh    # owner rwx, group/other r-x
chmod 644 config.txt   # owner rw, group/other r
```

### GOTCHA — bits mean different things on directories

| bit | file | **directory** |
|-----|------|---------------|
| r   | read contents | list names (`ls`) |
| w   | modify contents | create/delete/rename entries inside |
| x   | execute as program | **traverse** — `cd`, access anything inside |

So `r` without `x` on a dir is near-useless: you can see names but can't `stat`, `cat`,
or `cd` into anything (`ls -l` shows metadata as `?`). And `--x` on a *script* means a
group member can **run it but not `cat` its source** (the kernel reads it for them).

The "first matching class wins": if you're the **owner**, only owner bits apply — group
bits don't add to them.

---

## 8. Processes, signals & concurrency — Modal named this too

```bash
ps aux                 # all processes
pgrep -c myapp         # count matching procs (cleaner than ps|grep|wc)
kill PID               # SIGTERM (15): polite, CATCHABLE — process can clean up
kill -9 PID            # SIGKILL (9): immediate, CANNOT be caught/ignored, no cleanup
kill -0 PID            # send nothing, just test if the process exists
cmd &                  # run in background
echo $!                # PID of most-recent background job
wait                   # block until all background children finish
jobs / fg / bg         # list / foreground / background; Ctrl+C=SIGINT, Ctrl+Z=suspend
```

Right way to stop something: **SIGTERM, wait, then SIGKILL**:

```bash
kill PID; sleep 5; kill -0 PID 2>/dev/null && kill -9 PID
```

### Concurrency & perf intuition (talk-through points)

**Parallel wall-clock ≈ the slowest job, not the sum.**

```bash
sleep 2 & sleep 2 & sleep 2 & wait   # ~2s total, not 6s
```

This is why you parallelize **I/O-bound** work (HTTP, disk) — you're waiting, not burning CPU.

**Bounded parallelism** with xargs (don't fork 10,000 jobs):

```bash
xargs -P8 -I{} curl -O {} < urls.txt   # ≤8 concurrent; -P0 = unlimited (careful)
```

**Why a per-item loop is slow:** every external command = a `fork`+`exec` (~ms each).
A loop calling `wc`/`grep` once per line spawns N processes; one tool over the whole input
spawns one. Measured ~600× on 1000 lines.

```bash
while read l; do echo "$l" | wc -c; done < big   # 1000 forks  — slow
awk '{t+=length($0)+1} END{print t}' big          # 1 process  — fast
```

---

## 9. Variables, quoting & scripting

```bash
name=Alice             # NO spaces around = (name = Alice runs a command "name")
export API_KEY=abc     # add to environment for child processes
API_KEY=abc cmd        # set for ONE command only
echo "$HOME"           # double quotes: $vars expand
echo '$HOME'           # single quotes: fully literal, no expansion
echo $PATH             # dirs searched for commands (cwd is NOT in it → need ./script)
which python           # where a command resolves
```

### GOTCHA — quote your variables (the #1 broken-script bug)

```bash
file="my report.txt"
wc -w $file     # → tries "my" and "report.txt" (word-split). rm $file is the scary one.
wc -w "$file"   # → correct, one argument
```

- `"$@"` expands each arg as its own quoted word — the **only** correct way to forward args.
- `"$*"` joins all args into one string. `$@`/`$*` unquoted both word-split.
- Unmatched glob (`*.xyz`, no match) stays **literal** by default (`shopt -s nullglob` → empty).
- **Never `for f in $(ls)`** — parses ls output, word-splits on spaces. Use `for f in *`.

### Reading from files & subshell scope

```bash
while IFS= read -r line; do ...; done < file   # IFS= keeps whitespace; -r keeps backslashes
cat file | while read l; do count=$((count+1)); done   # ⚠️ loop runs in a SUBSHELL,
                                                        #    count is lost afterwards
```

Use `< file` (or `< <(cmd)` process substitution), not `cmd | while`, when you need
variables to survive the loop.

### Running scripts & the shebang

```bash
bash script.sh   # bash reads the file → only needs READ permission, ignores shebang
./script.sh      # OS executes directly → needs EXECUTE bit + a valid shebang
#!/usr/bin/env bash   # portable shebang: finds bash on $PATH
```

`./script.sh` failing usually means: not executable (`chmod +x`), no/bad shebang, or
cwd isn't where you think.

### Parameter expansion (read-it-fast reference)

```bash
${#f}            # length
${f:-default}    # use default if unset/empty (dodges set -u)
${f:?msg}        # abort with msg if unset/empty  (great guard before rm -rf)
${f#*.}  ${f##*.}   # strip shortest / longest prefix matching glob  (→ ext)
${f%.*}  ${f%%.*}   # strip shortest / longest suffix              (→ basename)
```

---

## 10. The "talk through it" checklist (the actual interview skill)

For any snippet they show you, say:

1. **What** each command + flag does.
2. **What flows** in (stdin) and out (stdout vs stderr vs file vs next command).
3. **What it prints / its exit code.**
4. **What's the gotcha / edge case** (spaces in names, empty var, no match, ordering…).
5. **How you'd test or fix it.**
