# Slice 6 — Permissions, processes & concurrency

## Quick intro (cheat-sheet)

### Permissions

| Command / concept | What it does |
|---|---|
| `ls -l` | Long listing: shows mode, link count, owner, group, size, mtime, name |
| `-rwxr-xr-x` | Mode string: file type `-`, then owner/group/other in rwx triplets |
| `r=4, w=2, x=1` | Octal values; add them per triplet: `rwx=7`, `r-x=5`, `r--=4` |
| `chmod 755 file` | Owner: rwx (7), group: r-x (5), other: r-x (5) |
| `chmod 644 file` | Owner: rw- (6), group: r-- (4), other: r-- (4) — typical for data files |
| `chmod 600 file` | Owner: rw- (6), group: --- (0), other: --- (0) — private keys / secrets |
| `chmod 751 file` | Owner: rwx (7), group: --x (1), other: --x (1) |
| `chmod +x file` | Add execute for **all three** classes (owner, group, other) |
| `chmod u+x file` | Add execute for owner only |
| `chmod u+x,go-w file` | Symbolic: add x for user, remove w for group and other |
| `x` on a **file** | Permission to **execute** it as a program |
| `x` on a **directory** | Permission to **traverse / enter** it (`cd` into it, open files inside) |
| `r` on a **directory** | Permission to **list** filenames (`ls dir`) |
| `w` on a **directory** | Permission to **create/delete** entries inside it |
| `chown user:group file` | Change owner and group of a file |
| `umask 022` | Default permissions mask: new files = 666−022 = 644; dirs = 777−022 = 755 |

### Processes & signals

| Command / concept | What it does |
|---|---|
| `ps aux` | Snapshot of all processes: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND |
| `ps -ef` | Same snapshot, different columns (UID PID PPID C STIME TTY TIME CMD) |
| `pgrep bash` | Print PIDs of processes matching name — no need to grep `ps` output |
| `pkill bash` | Send SIGTERM to all processes matching name |
| `kill PID` | Send **SIGTERM** (15) — politely asks process to clean up and exit |
| `kill -9 PID` | Send **SIGKILL** — OS force-kills; process cannot catch or ignore it |
| `kill -INT PID` | Send **SIGINT** — same as Ctrl-C; catchable |
| `kill -HUP PID` | Send **SIGHUP** — historically "terminal hangup"; many daemons reload config on HUP |
| SIGTERM | Catchable; process can do cleanup; default for `kill` |
| SIGKILL | **Not** catchable, not ignorable, not deferrable — last resort |
| SIGINT | Catchable; sent by Ctrl-C |
| SIGHUP | Catchable; sent when controlling terminal closes |

### Concurrency & performance

| Command / concept | What it does |
|---|---|
| `cmd &` | Run `cmd` in the background; shell returns immediately |
| `$!` | PID of the most recently backgrounded process |
| `wait` | Block until **all** background children finish |
| `wait $PID` | Block until that specific background PID finishes |
| `cmd1 & cmd2 & wait` | Run both in parallel; total time ≈ max(t1, t2) |
| `xargs -P4 -I{} cmd {}` | Run up to 4 copies of `cmd` in parallel (bounded parallelism) |
| pipe stages | Each stage in `a \| b \| c` is a **separate process running concurrently** |
| `( cmd )` | Subshell: runs in a forked child; variable changes do NOT propagate back |
| `{ cmd; }` | Command group: runs in the **current** shell; variable changes persist |
| fork/exec overhead | Every external command launch = fork + exec syscalls; in a tight loop this adds up |
| loop vs bulk | `for f in *; do grep x "$f"; done` spawns N greps; `grep x *` spawns one |

---

## Classic gotchas

- **`x` on a directory is not "execute"** in the file sense — it means *traverse*. Without `x` you cannot `cd` into it or open any file inside, even if you have `r` (which only lets you see names). With `r` but without `x`, `ls dir` shows filenames but `ls -l dir` shows `?` for all metadata.
- **`chmod +x` touches all three classes** (owner, group, other). If you only want the owner to run it, use `chmod u+x`.
- **`kill PID` is SIGTERM, not SIGKILL** — it asks nicely. A process can catch, ignore, or delay it. Use `kill -9` only when the process won't respond to SIGTERM.
- **`kill -9` is the last resort** — it leaves no chance for cleanup (open files, locks, temp files stay dirty). Prefer SIGTERM first, wait briefly, then escalate.
- **Subshell `( )` variables vanish** — if you set a variable inside `( )`, the parent shell never sees it. Use `{ }` when you need the change to persist.
- **Parallel wall-clock ≈ slowest job, not sum** — three `sleep 2 &` + `wait` takes ~2 s total, not 6 s. This is the key intuition for parallel speedup.

---

## Exercises

Try each before peeking at answers.md.

### Read — what does this mean / do / print?

**1.** Given this `ls -l` output:
```
-rwxr-xr-x 1 alice devs 1024 Jun 1 10:00 deploy.sh
```
Who can do what? Break down the permission string for owner (`alice`), group (`devs`), and other.

**2.** The repo's own `script.sh` has mode `751`. Run:
```bash
ls -l /home/musel/Github/bash-prep/script.sh
```
What does `-rwx--x--x` mean for owner, group, and other? Can a user in the `musel` group read the file's contents?

**3.** What does this print, and why?
```bash
touch secretkey
chmod 600 secretkey
ls -l secretkey
```

**4.** A directory has permissions `drw-r--r--` (no `x` for anyone). You run:
```bash
ls trapped/
ls -l trapped/
cat trapped/file.txt
```
Which commands succeed, which fail, and why?

**5.** What does this snippet do? How many jobs run at the same time, and roughly how long does it take?
```bash
sleep 2 &
sleep 2 &
sleep 2 &
wait
```

**6.** What is the difference between these two signals, and which one can a process ignore?
```bash
kill 1234        # (a)
kill -9 1234     # (b)
```

**7.** What does `$!` refer to, and what does this do?
```bash
sleep 99 &
echo "PID: $!"
kill $!
```

**8.** Why is the second command faster than the first, even though both search for the same pattern in the same files?
```bash
# (a)
for f in *.txt; do grep "hello" "$f"; done

# (b)
grep "hello" *.txt
```

### Write — how would you …?

**9.** Make a script `deploy.sh` executable by everyone, but writable only by the owner. Write the `chmod` command using octal.

**10.** You need a private SSH key file that only the owner can read or write (no permissions for group or other). Write the `chmod` command.

**11.** You have 100 URLs in `urls.txt`, one per line. You want to `curl` each URL but only run 8 downloads at a time to avoid hammering the server. Write the one-liner using `xargs`.

**12.** A process is running but ignoring `kill PID` (SIGTERM). What do you do next? Write the commands, explaining why you escalate.

**13.** You backgrounded three jobs and stored their PIDs. Write a snippet that starts three `curl` downloads in parallel and waits for all of them before continuing.
