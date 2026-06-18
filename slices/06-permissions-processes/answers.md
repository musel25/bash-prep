# Slice 6 — Answers

---

## 1. `ls -l` breakdown: `-rwxr-xr-x`

```
-  rwx  r-x  r-x
│   │    │    └─ other: read + execute
│   │    └────── group (devs): read + execute
│   └─────────── owner (alice): read + write + execute
└─────────────── file type: `-` = regular file
```

**Owner (`alice`):** can read, write, and execute the file.
**Group (`devs`):** can read and execute; cannot write.
**Other (everyone else):** can read and execute; cannot write.

*Why it matters:* the write bit on a script is separate from execute — you can run something you can't edit, which is normal for production binaries.

---

## 2. `script.sh` mode 751 (`-rwx--x--x`)

Real output:
```
$ ls -l /home/musel/Github/bash-prep/script.sh
-rwx--x--x 1 musel musel 67 Jun 17 20:15 /home/musel/Github/bash-prep/script.sh
```

Breakdown:
```
-  rwx  --x  --x
│   │    │    └─ other: execute only
│   │    └────── group: execute only
│   └─────────── owner (musel): read + write + execute
└─────────────── regular file
```

**Owner (`musel`):** full access — can read, modify, and run it.
**Group members:** can *execute* the script but **cannot read its source**. They can run it (the kernel reads it on their behalf), but they cannot `cat` or copy it.
**Other:** same as group — execute only, no read/write.

*Edge case:* "can a group member read the file?" — No. `--x` means execute only. `cat script.sh` would get `Permission denied`.

---

## 3. Directory `drw-r--r--` (no `x`)

Real experiment:
```bash
$ mkdir trapped && touch trapped/file.txt && chmod 644 trapped
$ ls trapped
file.txt          # succeeds — r lets you read the directory's name list

$ cat trapped/file.txt
cat: trapped/file.txt: Permission denied (os error 13)   # fails — no x means no traverse

$ ls -l trapped
total 0
-????????? ? ? ? ?            ? file.txt   # r without x: names visible, metadata is ?
```

**`ls trapped/`** — succeeds: `r` on a directory lets you read the list of filenames.
**`ls -l trapped/`** — partially works: filenames visible but all metadata shown as `?` because fetching inode metadata requires traversal (`x`).
**`cat trapped/file.txt`** — fails: the path lookup must traverse the directory, which requires `x`.

*The gotcha:* `r` without `x` is almost useless on a directory — you can see that files exist but you cannot access any of them.

---

## 4. Three parallel `sleep 2 &` + `wait`

```bash
sleep 2 &
sleep 2 &
sleep 2 &
wait
```

Real timing:
```
real    0m2.003s
user    0m0.003s
sys     0m0.003s
```

**All three run in parallel.** The shell backgrounds each `sleep 2` without waiting, then `wait` blocks until all three children finish. Since all three sleep for the same 2 seconds simultaneously, wall-clock time ≈ 2 s — not 6 s.

*Parallel speedup intuition:* total time ≈ duration of the **slowest** job, not the sum. This is the core reason to parallelize I/O-bound work (HTTP fetches, file copies) — you're waiting for the network/disk, not burning CPU.

---

## 5. `kill PID` vs `kill -9 PID`

**(a) `kill 1234`** — sends **SIGTERM** (signal 15). This is a polite request: "please clean up and exit." The process **can catch it**, run cleanup handlers, flush buffers, remove lock files, and then exit gracefully — or it can ignore it entirely.

**(b) `kill -9 1234`** — sends **SIGKILL** (signal 9). The OS terminates the process immediately. The process **cannot** catch, block, or ignore SIGKILL. No cleanup runs.

**Which can a process ignore?** SIGTERM can be caught or ignored. SIGKILL cannot.

*Best practice:* always try SIGTERM first, give the process a few seconds, then escalate to SIGKILL if it hasn't exited. Jump straight to `-9` and you risk dirty state (incomplete writes, unreleased locks, orphaned temp files).

---

## 6. `$!` and killing the background job

```bash
sleep 99 &
echo "PID: $!"
kill $!
```

Real output:
```
Background PID is: 33615
Killed it, exit status: 0
```

**`$!`** is a special shell variable that holds the PID of the **most recently backgrounded** process. It's only valid immediately after `&` — the next backgrounded command overwrites it.

This snippet: (1) starts `sleep 99` in the background, (2) prints its PID, (3) sends it SIGTERM. The `sleep` exits immediately. `kill` returns exit code 0 on success.

*How to test:* run `ps aux | grep sleep` before and after — the process disappears after `kill $!`.

---

## 7. `for` loop grep vs `grep *.txt`

```bash
# (a) — for loop
for f in *.txt; do grep "hello" "$f"; done

# (b) — single grep
grep "hello" *.txt
```

Real timing with 5 files:
```
--- for loop ---
real    0m0.004s

--- single grep ---
real    0m0.001s
```

**Why (b) is faster:** every external command invocation costs a **fork + exec** syscall pair. Command (a) spawns one new `grep` process per file — 5 files = 5 fork/exec pairs. Command (b) starts a single `grep` process and passes all filenames as arguments; `grep` opens them internally without any additional process creation.

*The gap widens with scale:* for 1000 files, the loop spawns 1000 processes. The single `grep` does the same work with 1. For CPU-bound tasks or huge input sizes the difference becomes dramatic.

*Note:* the for-loop pattern is sometimes necessary (e.g., when filenames contain spaces and the tool doesn't accept multiple args), but reach for bulk invocation first.

---

## 8. `deploy.sh` — executable by all, writable only by owner

```bash
chmod 755 deploy.sh
```

Real output after running:
```
$ touch deploy.sh && chmod 755 deploy.sh && ls -l deploy.sh
-rwxr-xr-x 1 musel musel 0 Jun 18 14:07 deploy.sh
```

755 = owner: rwx (7), group: r-x (5), other: r-x (5).

*Edge-case test:* after `chmod 755`, verify with `ls -l` that the write bit (`w`) is absent for group and other. If you use `chmod +x` instead of `755`, you may leave write bits in place from whatever umask created the file.

---

## 9. `xargs -P8` for parallel curl

```bash
xargs -P8 -I{} curl -O {} < urls.txt
```

Or equivalently:
```bash
cat urls.txt | xargs -P8 -I{} curl -O {}
```

`-P8` runs up to 8 `curl` processes at a time. As each one finishes, `xargs` starts the next until the input is exhausted.

Real timing intuition: 8 parallel downloads from a remote server that each take 1 s → total wall time ≈ ⌈100/8⌉ × 1 s ≈ 13 s instead of 100 s.

*Edge case:* `-I{}` combined with `-P` can behave unexpectedly if URLs contain special characters. Use `--null` / `print0` + `xargs -0` if filenames might have spaces. Also: `-P0` means "unlimited parallelism" — use carefully.

---

## 10. Escalating from SIGTERM to SIGKILL

```bash
# Step 1: politely ask
kill 1234

# Step 2: give it a moment to clean up
sleep 3

# Step 3: verify it's still alive
kill -0 1234 2>/dev/null && echo "still running, escalating..."

# Step 4: force-kill
kill -9 1234
```

`kill -0 PID` sends no signal but returns exit code 0 if the process exists — a safe way to check liveness.

*Why the two-step approach:* SIGTERM allows the process to flush write buffers, release file locks, remove PID files, and close network connections cleanly. Jumping straight to SIGKILL risks data corruption or stale locks that block future starts.

*Edge case:* a process can also be in an uninterruptible sleep state (D state in `ps` STAT column — typically waiting on a stuck kernel I/O operation). In that state even `kill -9` won't work until the I/O completes or times out. Check `ps aux` for `D` in the STAT column.
