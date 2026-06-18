# Slice 4 — Find & filter

## Quick intro (cheat-sheet)

### grep flags
| Flag | What it does |
|------|-------------|
| `-i` | Case-insensitive match |
| `-v` | Invert — print lines that do NOT match |
| `-n` | Prefix each match with its line number |
| `-c` | Print count of matching lines (not the lines themselves) |
| `-r` | Recurse into subdirectories |
| `-l` | Print only filenames that contain a match |
| `-E` | Extended regex (enables `+`, `?`, `\|`, `()` without backslash) |
| `-o` | Print only the matched portion, one match per line |
| `-w` | Match whole words only (word boundary on both sides) |
| `-F` | Treat pattern as literal string, no regex |

### Regex anchors
| Pattern | Meaning |
|---------|---------|
| `^` | Start of line |
| `$` | End of line |
| `.` | Any single character (including literal `.`) |

### find flags
| Expression | What it does |
|------------|-------------|
| `-name '*.txt'` | Match filename glob (case-sensitive) |
| `-iname '*.TXT'` | Match filename glob (case-insensitive) |
| `-type f` | Files only |
| `-type d` | Directories only |
| `-maxdepth N` | Don't descend past N directory levels |
| `-mtime -N` | Modified fewer than N days ago |
| `-mtime +N` | Modified more than N days ago |
| `-size +Mk` | Larger than M kilobytes (use `M` for megabytes) |
| `-exec cmd {} \;` | Run `cmd` once per file; `{}` is replaced by the path |
| `-exec cmd {} +` | Run `cmd` once with all matching files batched as arguments |
| `-print0` | Print paths separated by null byte `\0` instead of newline |

### xargs
| Form | What it does |
|------|-------------|
| `xargs cmd` | Pass stdin lines as arguments to `cmd` |
| `xargs -I{}` | Replace `{}` in the command template per input line |
| `xargs -n N` | Pass at most N arguments per invocation |
| `xargs -0` | Read null-delimited input (pair with `find -print0`) |

### sort
| Flag | What it does |
|------|-------------|
| (none) | Lexicographic (alphabetical) sort — default |
| `-n` | Numeric sort |
| `-r` | Reverse order |
| `-k N` | Sort by field N (whitespace-delimited) |

### uniq
| Flag | What it does |
|------|-------------|
| (none) | Collapse adjacent duplicate lines |
| `-c` | Prefix each line with its count |

---

## Classic gotchas

- **`sort` is lexicographic by default.** `8`, `9`, `10`, `100` sorts as `10 100 8 9`. You need `-n` for numeric order. Interviewers love pasting a pipeline that counts and ranks without `-n` and asking what the output is.

- **`uniq` only collapses *adjacent* duplicates.** If the file is not sorted first, repeated words scattered across lines will not be merged. You almost always want `sort | uniq`, not bare `uniq`.

- **`find … | xargs` breaks on filenames with spaces or newlines.** xargs splits on whitespace by default. A file called `feb report.txt` becomes two arguments: `feb` and `report.txt`. Fix: `find … -print0 | xargs -0`.

- **`grep "c.t"` matches `cat`, `cot`, `c.t`, and `cbt`.** The dot is a regex metacharacter (any character). To match a literal dot, escape it (`c\.t`) or use `grep -F`.

- **`-exec {} \;` vs `-exec {} +`.** `\;` calls the command once per file (N processes). `+` batches all results into one call (1 process, like xargs). Using `\;` with slow commands on thousands of files can be unexpectedly expensive.

---

## Exercises

Try each before peeking at answers.md.

---

### Read — what does this do / print?

**1.**
```bash
printf "connected from 10.0.0.1\nfailed from 192.168.1.5\nlocal 127.0.0.1\n" > /tmp/access.log
grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" /tmp/access.log
```
What does this print? What would change if you dropped the `-o`?

---

**2.**
```bash
printf "8\n10\n9\n100\n2\n" > /tmp/scores.txt
sort /tmp/scores.txt
```
What is the output? Is it correct if you wanted numbers in ascending order?

---

**3.**
```bash
printf "apple\nbanana\napple\nbanana\nbanana\napple\n" > /tmp/fruit_counts.txt
uniq -c /tmp/fruit_counts.txt
```
What does this print? How many distinct values do you expect?

---

**4.**
```bash
mkdir -p /tmp/reports
touch "/tmp/reports/jan.txt" "/tmp/reports/feb report.txt"
find /tmp/reports -name "*.txt" | xargs wc -l
```
Does this work? What happens and why?

---

**5.**
```bash
mkdir -p /tmp/logs
touch /tmp/logs/a.log /tmp/logs/b.log /tmp/logs/c.log
find /tmp/logs -name "*.log" -exec echo "processing" {} \;
find /tmp/logs -name "*.log" -exec echo "processing" {} +
```
What is different about the two `find` commands? How many times is `echo` called in each case?

---

**6.**
```bash
printf "python\nbash\npython\ngo\nbash\npython\nrust\ngo\nbash\npython\n" > /tmp/langs.txt
sort /tmp/langs.txt | uniq -c | sort -nr
```
What does this print? Name the three-stage idiom.

---

**7.**
```bash
printf "c.t\ncat\ncot\n" > /tmp/dotfile.txt
grep "c.t" /tmp/dotfile.txt
```
How many lines match? Which ones, and why might that surprise you?

---

### Write — how would you …?

**8.** List every `.py` file under `/home/musel/Github/bash-prep` that contains the word `error` (case-insensitive). Print only the filenames, not the matching lines.

**9.** Find all regular files in `/var/log` modified in the last 7 days and larger than 10 MB. Print only their paths.

**10.** Count how many times each HTTP status code appears in a log file `/tmp/access.log` where each line ends with a three-digit code (e.g. `200`, `404`, `500`). Output should be sorted highest-count first.

**11.** You have a directory `/tmp/data` with filenames that may contain spaces. Safely delete every `.csv` file in it (without touching other files). Use `find` with `-print0` and `xargs -0`.
