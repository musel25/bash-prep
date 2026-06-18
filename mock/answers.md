# Mock bank — Answers

---

### 1. `ps aux | grep myapp | wc -l` — (easy)

**What it intends:** Count running processes matching "myapp".

**The bug:** `grep myapp` matches its own process entry in the `ps` output. When you run `ps aux | grep myapp`, the `grep myapp` process itself appears as a line containing "myapp", so the count is always inflated by at least 1.

**Real output (sleep used as a stand-in for an actual process):**

```
$ ps aux | grep sleep | wc -l
4    ← includes the grep process itself and shell wrappers
```

**Fixes:**
- `grep -v grep` to filter out the grep line: `ps aux | grep myapp | grep -v grep | wc -l`
- Use `pgrep` instead: `pgrep -c myapp` — this is the cleanest approach
- Bracket trick: `grep '[m]yapp'` — the pattern `[m]yapp` matches "myapp" but the grep command line reads `[m]yapp`, which doesn't match itself

**Edge cases:**
- What if no process is running? `wc -l` returns 0 (with the `grep -v grep` fix), but 1 without it — the naive version can never return 0.
- Process names truncated by ps on some systems.
- `pgrep -c` exits with code 1 when no match; `grep | wc -l` always exits 0.

---

### 2. `for f in $(ls); do cp "$f" /backup/; done` — (med)

**What it intends:** Copy every file in the current directory to `/backup/`.

**The bug:** `$(ls)` undergoes word-splitting on whitespace. A filename like `hello world.txt` becomes two tokens: `hello` and `world.txt`. Both fail to copy (or worse, copy wrong files).

**Real output:**

```
$ ls testdir/
'hello world.txt'  normal.txt

$ for f in $(ls); do echo "[$f]"; done
[hello]
[world.txt]
[normal.txt]
```

`hello` and `world.txt` are treated as separate filenames — neither exists.

**Fix:** Use a shell glob instead of `$(ls)`:

```bash
for f in *; do
    cp "$f" /backup/
done
```

```
$ for f in *; do echo "[$f]"; done
[hello world.txt]
[normal.txt]
```

The glob expands correctly and the shell never splits on spaces inside filenames.

**Edge cases:**
- Hidden files (dotfiles): `*` skips them unless you add `.[!.]*` or set `dotglob`.
- Empty directory: `*` expands to the literal string `*` if no files match (unless `nullglob` is set in bash). Guard with `[ -e "$f" ]` or `shopt -s nullglob`.
- `ls` output is for humans, not scripts. Never parse `ls`.

---

### 3. Redirection ordering trap — (med)

**Version A:** `ls /nonexistent 2>&1 > output.txt`
**Version B:** `ls /nonexistent > output.txt 2>&1`

**Answer: Version B is correct.**

Shell redirections are evaluated left to right. In version A:
1. `2>&1` — at this moment, stdout is still the terminal, so stderr is redirected to the terminal too.
2. `> output.txt` — stdout is now redirected to the file. But stderr already points to the old terminal.

Result: the error message goes to the terminal; `output.txt` is empty.

In version B:
1. `> output.txt` — stdout goes to the file.
2. `2>&1` — stderr is redirected to wherever stdout now points (the file).

Result: both stdout and stderr land in `output.txt`.

**Real output:**

```
# Version A (wrong order)
$ ls /nonexistent 2>&1 > output.txt
ls: cannot access '/nonexistent': No such file or directory   ← prints to terminal
$ cat output.txt
                                                               ← empty

# Version B (correct order)
$ ls /nonexistent > output.txt 2>&1
$ cat output.txt
ls: cannot access '/nonexistent': No such file or directory   ← in the file
```

**Mnemonic:** "redirect stdout first, then point stderr at it."

---

### 4. Permissions question — (easy)

```
-rwxr-xr-- 1 alice devs 4096 Jun 18 09:00 deploy.sh
```

You are `bob`, member of group `devs`.

**Breakdown:**
- `-` = regular file
- `rwx` = owner (alice): read, write, execute
- `r-x` = group (devs): read, no write, execute
- `r--` = other: read only, no execute

**As bob (in the devs group):** The group bits apply. `r-x` = bob **can read** and **can execute** `deploy.sh`. Bob cannot write to it.

**Edge cases:**
- If bob were also alice, the owner bits apply (most restrictive interpretation: the *first* matching category wins — owner, then group, then other). If you're the owner, group bits don't apply.
- `execute` on a directory means "can traverse into it", not run it as a program.
- `setuid` (`s` in place of `x`) would run the script as the file's owner regardless of who calls it — important for privileged scripts.
- ACLs (`getfacl`) can override standard rwx.

---

### 5. `&` + `wait` parallelism — (med)

**Explanation step by step:**
1. `process_chunk 1 &` — forks a child process for chunk 1; shell continues immediately.
2. Same for chunks 2 and 3 — all three are now running concurrently.
3. `wait` — the parent shell blocks until **all** background jobs finish.
4. Elapsed time is recorded and printed.

**Expected elapsed time:** ~10 seconds (the time of the single slowest job), not 30 seconds. All three chunks overlap.

**Real output (with `sleep 1` as a stand-in for 10s jobs):**

```
$ start=$(date +%s); sleep 1 & sleep 1 & sleep 1 & wait; end=$(date +%s)
$ echo "$((end - start))s"
1s
```

**Edge cases:**
- One failing job: by default `wait` still waits for all others; exit code of `wait` is the exit code of the last job waited on. Use `wait -n` (bash 4.3+) to wait for the first job to finish and check its status.
- Unbounded parallelism: if you fork 10,000 jobs, you'll exhaust file descriptors and memory. Use a semaphore pattern (e.g. xargs -P N) to cap concurrency.
- `wait $PID` waits for a specific child; bare `wait` waits for all.
- Order of completion is non-deterministic — shown in the real output where task2 finished before task1.

---

### 6. `sort | uniq -c | sort -nr | head -10` — (easy)

**Explanation step by step:**
1. `cat access.log` — print the file to stdout (the `cat` here is a "useless cat"; `sort access.log` works directly).
2. `sort` — sort all lines lexicographically so identical lines are adjacent.
3. `uniq -c` — collapse consecutive duplicate lines, prefixing each with its count.
4. `sort -nr` — sort numerically (`-n`) in reverse (`-r`) — highest count first.
5. `head -10` — take the top 10.

**Real output:**

```
$ printf 'apple\nbanana\napple\napple\nbanana\ncherry\n' | sort | uniq -c | sort -nr | head -3
      3 apple
      2 banana
      1 cherry
```

**Adapted for IPs (first field only):**

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -10
```

**Edge cases:**
- `uniq` only collapses *adjacent* duplicates — the `sort` before it is mandatory.
- If lines have leading/trailing whitespace, `uniq -c` won't collapse them.
- Very large files: `sort` spills to disk (uses `/tmp`); `awk` for frequency with arrays can be faster and avoids the sort.

---

### 7. `awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -5` — (med)

**Explanation step by step:**
1. `awk '{print $1}'` — for each line in `access.log`, print the first whitespace-delimited field (the IP address in a standard Apache/nginx log).
2. `sort` — sort IPs so duplicates are adjacent.
3. `uniq -c` — count consecutive duplicates.
4. `sort -nr` — sort by count, descending.
5. `head -5` — top 5 IPs.

**Real output (synthetic log):**

```
$ printf '192.168.1.1 GET /\n10.0.0.1 GET /api\n192.168.1.1 POST /data\n10.0.0.2 GET /\n192.168.1.1 GET /home\n' \
  | awk '{print $1}' | sort | uniq -c | sort -nr | head -3
      3 192.168.1.1
      1 10.0.0.2
      1 10.0.0.1
```

**Edge cases:**
- Lines with no whitespace (malformed log entries): `$1` returns the whole line — won't break, but inflates the count for a junk key.
- IPv6 addresses may contain spaces if log format wraps fields — need a different delimiter.
- Alternative using pure awk (avoids sort+uniq):
  ```bash
  awk '{count[$1]++} END {for (ip in count) print count[ip], ip}' access.log | sort -nr | head -5
  ```
  This is O(n) in memory for unique IPs rather than O(n log n) sort.

---

### 8. `set -e` surprise with `if` — (hard)

**What prints:**

```
script finished
```

**The surprise:** `set -e` does *not* cause the script to exit when a command used as an `if` condition (or in `while`/`until`) returns non-zero. The `grep -q "ERROR" app.log` fails (exit code 1, no match), the `if` branch is simply not taken, and execution continues normally.

`set -e` triggers on an unchecked non-zero exit — but commands in an `if` condition are always "checked" (the shell uses their exit status to decide the branch). The same exemption applies to `||`, `&&`, and `!`.

**Real output:**

```
$ cat app.log     # no ERROR lines
$ bash -c '
set -e
run_checks() { grep -q "ERROR" app.log; }
if run_checks; then echo "errors found"; fi
echo "script finished"
'
script finished
```

**Edge cases:**
- If you call `run_checks` *outside* an `if`, a failing return *would* trigger `set -e` and exit the script.
- `set -e` does not propagate into subshells by default in all contexts.
- Functions called with `if`, `||`, `&&` are fully shielded from `set -e`.
- Combined with `set -o pipefail` for better coverage — but even then, `if` conditions are exempt.

---

### 9. `set -e` vs `set -e` + `set -o pipefail` — (hard)

**Version A** (set -e only):

```
$ bash -c 'set -e; false | true; echo "still running"'
still running
```

The pipeline exit code is the exit code of its **rightmost** command (`true`, which is 0). `set -e` sees exit code 0 and does not abort. The `false` failure is silently swallowed.

**Version B** (set -e + pipefail):

```
$ bash -c 'set -e; set -o pipefail; false | true; echo "still running"'
# (nothing printed — script exited)
$ echo "exit: $?"
exit: 1
```

With `pipefail`, the pipeline exits non-zero if *any* command in it fails. `false` exited 1, so the pipeline exits 1, and `set -e` aborts the script.

**Answer: Version B is more correct** for scripts where silent failures in the middle of a pipeline are bugs — which is almost always.

**Edge cases:**
- `pipefail` changes the behavior of `grep ... | head`. When `head` exits (after reading enough lines), `grep` gets a SIGPIPE. With pipefail, this counts as a failure. Workaround: `grep ... | head || true`.
- `set -o pipefail` is not POSIX — it's a bash extension.
- Best practice: `set -euo pipefail` at the top of every script.

---

### 10. `cut` with missing delimiter — (med)

**Explanation step by step:**

```bash
echo "root:x:0:0:root:/root:/bin/bash" | cut -d: -f7
```

1. `-d:` sets `:` as the delimiter.
2. `-f7` selects the 7th field.
3. Output: `/bin/bash`

```bash
echo "no-colons-here" | cut -d: -f2
```

1. `-d:` sets `:` as delimiter.
2. The input has no `:`, so there is only one field (field 1).
3. `-f2` requests field 2 — which doesn't exist.
4. `cut` outputs **the whole line** rather than an empty string.

**Real output:**

```
$ echo "root:x:0:0:root:/root:/bin/bash" | cut -d: -f7
/bin/bash

$ echo "no-colons-here" | cut -d: -f2
no-colons-here
```

**Edge cases:**
- `cut` prints the whole line when the delimiter is absent — this is a silent failure that produces misleading output.
- Trailing delimiters: `a:b:` has an empty field 3 — `cut` returns empty string, which is correct.
- Alternative: `awk -F: '{print $7}'` returns an empty string when field 7 doesn't exist — safer for scripting.
- `cut -f-3` (fields 1 through 3) and `cut -f3-` (field 3 to end) are useful range selectors.

---

### 11. Dangerous `rm` with unset variable — (hard)

```bash
DIR=$1
rm -rf ${DIR}/cache
```

**The bug:** If `$1` is empty (script called with no argument), `DIR` is empty, and the command becomes:

```bash
rm -rf /cache
```

or, if `/cache` doesn't exist but the working directory matters, it could be `rm -rf cache` — removing a local directory named `cache`. In the worst case with `DIR` set to a blank that expands before a slash that you control: `rm -rf /important_data`.

**Real expansion:**

```
$ DIR=""
$ echo "rm -rf ${DIR}/cache"
rm -rf /cache
```

**Fixes:**

```bash
# 1. Require the argument
DIR="${1:?Error: DIR must be set}"

# 2. Guard explicitly
if [[ -z "$DIR" ]]; then
    echo "DIR is empty, aborting" >&2
    exit 1
fi

# 3. set -u to catch unset variables
set -u
DIR=$1  # will abort if $1 is unset
```

**Edge cases:**
- `${DIR}/cache` with `DIR=/` becomes `rm -rf //cache` — mostly harmless, but `DIR=/home/user` with a typo in `cache` could be catastrophic.
- Always double-quote: `rm -rf "${DIR}/cache"` prevents glob expansion in the path.
- Consider `rm -rf -- "${DIR}/cache"` to guard against paths starting with `-`.

---

### 12. `kill` vs `kill -9` — (med)

**Version A: `kill $PID`**
Sends `SIGTERM` (signal 15) — a polite request to terminate. The process can catch this signal with a `trap`, perform cleanup (flush buffers, close sockets, remove temp files), and then exit gracefully.

**Real output (process with SIGTERM trap):**

```
$ trap "echo caught SIGTERM, cleaning up; exit 0" TERM
$ while true; do sleep 0.1; done &
$ kill $!
caught SIGTERM, cleaning up
```

**Version B: `kill -9 $PID`**
Sends `SIGKILL` (signal 9). The kernel delivers it directly — the process has no opportunity to catch, block, or ignore it. It is terminated immediately with no cleanup.

```
$ kill -9 $!
# (no cleanup message — process just vanishes)
```

**Answer: Use `kill` (SIGTERM) first. Use `kill -9` only as a last resort.**

Correct pattern:
```bash
kill $PID
sleep 5
kill -0 $PID 2>/dev/null && kill -9 $PID
```

**Edge cases:**
- Zombie processes can't be killed with any signal — they're already dead, waiting for their parent to `wait()` on them.
- `kill -0 $PID` checks if a process exists (sends no signal) — useful for polling.
- `SIGKILL` can still leave orphaned temp files, unclosed database connections, corrupted writes-in-progress.
- Containers: SIGTERM should be handled by the PID 1 process (entrypoint) to propagate to child processes.

---

### 13. Slow loop with per-line process spawn — (med)

**Why it's slow:** Every iteration of the loop spawns a new `wc` subprocess via `$(echo "$line" | wc -c)`. For a file with 1000 lines, this forks and exec's 1000 child processes. Process creation overhead (~2ms each on Linux) dominates over actual work.

**Real timing:**

```
# Loop approach: 1000 lines
Loop time: 2406ms

# Single awk: 1000 lines
Awk time: 4ms
```

That's a ~600x speedup.

**Fix:** Use a single tool that reads the whole file in one pass:

```bash
# Option 1: awk
total=$(awk '{total += length($0) + 1} END {print total}' bigfile.txt)

# Option 2: wc -c on the whole file
total=$(wc -c < bigfile.txt)
```

**Edge cases:**
- `wc -c < file` counts bytes including the final newline — usually what you want.
- The loop also uses `$(echo ...)` which adds another fork; `echo "$line" | wc -c` counts the newline that `echo` appends, so the byte count is off by 1 per line.
- General rule: if you're calling an external command inside a loop, ask whether the tool can process all lines at once (awk, sed, grep, sort — all can).

---

### 14. `grep -c` vs `grep | wc -l` — (med)

Both count matching lines. **`grep -c` is more correct.**

**Same result for matching lines:**

```
$ printf 'foo\nfoo\nbar\n' > testfile.txt
$ grep -c "foo" testfile.txt
2
$ grep "foo" testfile.txt | wc -l
2
```

**The critical difference — missing file:**

```
$ grep -c "foo" /nonexistent
grep: /nonexistent: No such file or directory
exit: 2           ← error propagates

$ grep "foo" /nonexistent | wc -l
grep: /nonexistent: No such file or directory
0
exit: 0           ← error swallowed; wc returns 0
```

With `grep | wc -l`, the pipe masks grep's non-zero exit. A script with `set -e` won't catch the error; the count silently returns 0 instead of failing.

**Answer: `grep -c` is more correct** — it propagates errors, is slightly faster (no fork for wc), and is semantically cleaner.

**Edge case:** `grep -c` returns exit code 1 when there are *zero* matches (not just on error). With `set -e`, `grep -c "pattern" file || true` is the safe idiom when 0 matches is a valid outcome.

---

### 15. Subshell variable scoping in pipe — (hard)

**Version A** always prints `Lines: 0`. Version B prints the correct count.

**Why:** In version A, `cat data.txt | while read line; do ... done` — the `while` loop runs in a *subshell* (the right-hand side of a pipe). Any variable assignments inside it are invisible to the parent shell. When the subshell exits, `count` in the parent is still 0.

**Real output:**

```
$ count=0; echo -e "a\nb\nc" | while read line; do count=$((count+1)); done; echo "Count: $count"
Count: 0

$ count=0; while IFS= read -r line; do count=$((count+1)); done < <(echo -e "a\nb\nc"); echo "Count: $count"
Count: 3
```

**Version B** uses process substitution (`< <(...)`) — the `while` loop runs in the *current* shell, so `count` is modified in place.

**Additional fixes:**
- `lastpipe` shell option (bash 4.2+): `shopt -s lastpipe` makes the last command in a pipeline run in the current shell.
- `wc -l < data.txt` if you just need a line count.

**Edge cases:**
- `IFS= read -r` is the correct idiom: `IFS=` prevents stripping leading/trailing whitespace; `-r` prevents backslash interpretation.
- Bare `read line` without `-r` will eat backslashes in line content.

---

### 16. `find -exec` vs `find | xargs` with spaces — (med)

**Version A:** `find . -name "*.log" -exec wc -l {} \;`
**Version B:** `find . -name "*.log" | xargs wc -l`

**The bug in version B:** `xargs` splits its input on whitespace by default. A filename like `my app.log` becomes two arguments: `my` and `app.log`. Both fail.

**Real output:**

```
# Directory contains "hello world.txt" and "normal.txt"

# Version B (broken):
$ find . -name "*.txt" | xargs ls -la
ls: cannot access './hello': No such file or directory
ls: cannot access 'world.txt': No such file or directory
normal.txt

# Version B fixed (-print0 | xargs -0):
$ find . -name "*.txt" -print0 | xargs -0 ls -la
-rw-r--r-- hello world.txt
-rw-r--r-- normal.txt
```

**Version A is safer** for filenames with spaces because `-exec` passes the filename as a single argument directly to the program.

**But:** Version A forks a new `wc` process for *each file* — slow for many files. The correct efficient+safe fix:

```bash
find . -name "*.log" -print0 | xargs -0 wc -l
```

Or use `find -exec ... {} +` (passes multiple files per invocation):

```bash
find . -name "*.log" -exec wc -l {} +
```

**Edge cases:**
- Filenames with newlines: `xargs -0` (null-delimited) handles them; newline-delimited pipes do not.
- `xargs` has a max argument length limit (ARG_MAX); `-print0 | xargs -0` still batches correctly.

---

### 17. `ls /nonexistent > output.txt 2>&1` — (easy)

**Explanation step by step:**
1. `ls /nonexistent` — lists a path that doesn't exist; ls writes an error to stderr, exits with code 2.
2. `> output.txt` — redirects stdout to the file.
3. `2>&1` — redirects stderr to wherever stdout currently points (the file).
4. Both stdout and stderr land in `output.txt`.
5. `echo "exit code: $?"` — prints `2` (ls's exit code).
6. `cat output.txt` — shows the error message.

**Real output:**

```
$ ls /nonexistent > output.txt 2>&1
$ echo "exit code: $?"
exit code: 2
$ cat output.txt
ls: cannot access '/nonexistent': No such file or directory
```

**How to test:**
```bash
# Verify file contains the error
grep -q "No such file" output.txt && echo "PASS" || echo "FAIL"
# Verify exit code was captured correctly
[[ $? -eq 2 ]] && echo "exit code correct"
```

**Edge cases:**
- `$?` must be read *immediately* after the command — any subsequent command overwrites it.
- If `output.txt` is in a directory you can't write to, the redirection itself fails; the error goes to the terminal and `$?` reflects the redirection failure.

---

### 18. `find | xargs rm` edge cases — (hard)

```bash
LOG_DIR="/var/log/myapp"
find "$LOG_DIR" -name "*.tmp" -mtime +7 | xargs rm -f
```

**Edge cases and problems:**

1. **Filenames with spaces or newlines:** `xargs` splits on whitespace — a file named `my log.tmp` becomes `my` and `log.tmp`. `rm` gets wrong paths, potentially deleting other files.

2. **Empty `LOG_DIR`:** If `LOG_DIR` is empty or unset, `find ""` searches the current directory and removes `.tmp` files wherever you happen to be running the script.

3. **Zero matches:** If `find` returns no files, `xargs rm -f` is called with no arguments — `rm -f` with no arguments exits 0 harmlessly, but it's worth noting. (Some `xargs` variants call the command with empty args; use `xargs --no-run-if-empty` or `-r` on GNU xargs.)

4. **Race condition:** Between `find` listing a file and `rm` removing it, another process could create a file with a path that now points elsewhere due to symlinks or mounts.

**Safer version:**

```bash
LOG_DIR="/var/log/myapp"
: "${LOG_DIR:?LOG_DIR must be set}"    # abort if empty
find "$LOG_DIR" -name "*.tmp" -mtime +7 -print0 | xargs -0 -r rm -f
```

Or even simpler with `-delete` (no xargs, no shell split):

```bash
find "$LOG_DIR" -name "*.tmp" -mtime +7 -delete
```

`-delete` is atomic per file and avoids the pipe entirely — preferred for destructive operations.
