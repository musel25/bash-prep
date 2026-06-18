# Slice 4 — Answers

---

### 1.

**Command:**
```bash
printf "connected from 10.0.0.1\nfailed from 192.168.1.5\nlocal 127.0.0.1\n" > /tmp/access.log
grep -oE "[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+" /tmp/access.log
```

**Output (verified in bash):**
```
10.0.0.1
192.168.1.5
127.0.0.1
```

**Why:** `-o` prints only the matched portion of each line, one match per line. `-E` enables extended regex so `+` (one or more) works without a backslash. Without `-o`, grep would print the entire matching line — useful when you want to extract structured tokens from noisy text.

**How to test:** Remove `-o` and observe that full lines print instead.

---

### 2.

**Command:**
```bash
printf "8\n10\n9\n100\n2\n" > /tmp/scores.txt
sort /tmp/scores.txt
```

**Output (verified in bash):**
```
10
100
2
8
9
```

**Why:** `sort` is **lexicographic by default** — it compares character by character, so `1` < `2` < `8` < `9`. `10` sorts before `2` because `'1' < '2'`. This is almost never what you want for numbers. Use `sort -n` for numeric order (`2 8 9 10 100`).

**How to test:** Run `sort -n /tmp/scores.txt` and compare.

---

### 3.

**Command:**
```bash
printf "apple\nbanana\napple\nbanana\nbanana\napple\n" > /tmp/fruit_counts.txt
uniq -c /tmp/fruit_counts.txt
```

**Output (verified in bash):**
```
      1 apple
      1 banana
      1 apple
      2 banana
      1 apple
```

**Why:** `uniq` collapses only **adjacent** duplicate lines. The input is not sorted, so `apple` and `banana` alternate — `uniq` sees each as a fresh value every time the line changes. The last two `banana` lines are adjacent, so they collapse to `2`. There are 5 output lines, not 2. To get a true count, sort first: `sort /tmp/fruit_counts.txt | uniq -c | sort -nr`.

**How to test:** Run `sort /tmp/fruit_counts.txt | uniq -c` — you should get `3 apple` and `3 banana`.

---

### 4.

**Command:**
```bash
mkdir -p /tmp/reports
touch "/tmp/reports/jan.txt" "/tmp/reports/feb report.txt"
find /tmp/reports -name "*.txt" | xargs wc -l
```

**Output (verified in bash):**
```
wc: /tmp/reports/feb: No such file or directory
wc: report.txt: No such file or directory
0 /tmp/reports/jan.txt
0 total
```
Exit code: `123` (partial failure)

**Why:** `find` outputs one path per line. `xargs` splits on whitespace. `"feb report.txt"` becomes two tokens: `/tmp/reports/feb` and `report.txt` — neither exists. The fix is `find /tmp/reports -name "*.txt" -print0 | xargs -0 wc -l`: `-print0` uses null bytes as separators and `-0` tells xargs to split on null bytes instead of whitespace.

**How to test:** Run the fixed version and confirm both files are counted.

---

### 5.

**Command:**
```bash
mkdir -p /tmp/logs
touch /tmp/logs/a.log /tmp/logs/b.log /tmp/logs/c.log
find /tmp/logs -name "*.log" -exec echo "processing" {} \;
find /tmp/logs -name "*.log" -exec echo "processing" {} +
```

**Output (verified in bash):**
```
processing /tmp/logs/c.log
processing /tmp/logs/b.log
processing /tmp/logs/a.log
processing /tmp/logs/c.log /tmp/logs/b.log /tmp/logs/a.log
```

**Why:** `-exec {} \;` calls `echo` **once per file** — 3 invocations, each receiving one path. `-exec {} +` calls `echo` **once total** with all matching paths batched as separate arguments — 1 invocation. The `+` form is like xargs: much faster when there are many files and the command is expensive to start (e.g., `gzip`, `rsync`). Note: the order of files is filesystem order, not alphabetical.

**How to test:** Replace `echo` with a command that prints its PID (`bash -c 'echo $$ "$@"' --`) to confirm invocation count.

---

### 6.

**Command:**
```bash
printf "python\nbash\npython\ngo\nbash\npython\nrust\ngo\nbash\npython\n" > /tmp/langs.txt
sort /tmp/langs.txt | uniq -c | sort -nr
```

**Output (verified in bash):**
```
      4 python
      3 bash
      2 go
      1 rust
```

**Why:** This is the classic **sort | uniq -c | sort -nr** top-N idiom.
1. `sort` groups identical lines adjacent to each other.
2. `uniq -c` counts and collapses each group.
3. `sort -nr` sorts numerically in reverse so the highest count is first.

The idiom works on any list of values — log levels, IP addresses, HTTP codes, etc.

**How to test:** Remove the first `sort` and observe that `uniq -c` gives wrong counts because lines are not adjacent.

---

### 7.

**Command:**
```bash
printf "c.t\ncat\ncot\n" > /tmp/dotfile.txt
grep "c.t" /tmp/dotfile.txt
```

**Output (verified in bash):**
```
c.t
cat
cot
```

**Why:** All three lines match. In regex, `.` is a metacharacter meaning **any single character**. So `c.t` matches `cat` (a), `cot` (o), and `c.t` (literal dot). There is no line like `cbt` here but that would also match. To match a literal dot only, use `grep 'c\.t'` or `grep -F 'c.t'`.

**How to test:** Add a line `cbt` — it matches. Run `grep -F 'c.t'` and confirm only `c.t` matches.

---

### 8.

```bash
grep -ril "error" /home/musel/Github/bash-prep --include="*.py"
```

**Why:** `-r` recurse, `-i` case-insensitive, `-l` list filenames only. `--include` limits which files grep searches (without it, grep reads every file it finds recursively). This is more direct than `find … | xargs grep`.

**Edge case / test:** Confirm a file containing `ERROR` (uppercase) appears in the output and a `.py` file without the word does not.

---

### 9.

```bash
find /var/log -type f -mtime -7 -size +10M
```

**Why:** `-type f` excludes directories; `-mtime -7` means modified fewer than 7×24 hours ago; `-size +10M` means strictly larger than 10 megabytes. Note: `find` size units are `c` (bytes), `k` (kB), `M` (MB), `G` (GB). Without `-type f`, directories could appear in results if they somehow matched size (they rarely do, but it's cleaner to be explicit).

**Edge case / test:** Run with `-mtime -1` first (recent files only) to confirm the filter works before widening the window.

---

### 10.

```bash
grep -oE "[0-9]{3}$" /tmp/access.log | sort | uniq -c | sort -nr
```

**Why:** `-oE "[0-9]{3}$"` extracts the three-digit code at the end of each line. Then the standard `sort | uniq -c | sort -nr` idiom ranks by frequency. If the log format has a trailing space or other character after the code, adjust the regex (e.g., `[0-9]{3}\b` or extract by field with `awk '{print $NF}'`).

**Edge case / test:** Add a line with `1234` at the end — confirm it does not match `[0-9]{3}$` (four digits, not three).

---

### 11.

```bash
find /tmp/data -name "*.csv" -print0 | xargs -0 rm
```

**Why:** `-print0` separates paths with null bytes so spaces in filenames are safe. `xargs -0` reads null-delimited input and passes all paths to a single `rm` call. Using plain `find … | xargs rm` would split `my data.csv` into `my` and `data.csv` and try to delete those (wrong files, or errors).

**Edge case / test:** Create a file `/tmp/data/my file.csv` and verify it is deleted. Check that a `.txt` file in the same directory is untouched.
