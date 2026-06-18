# Slice 5 — Answers

---

## Read exercises

### 1.
```
eng
mkt
eng
```
**Why:** `-d','` sets the delimiter to comma; `-f2` picks the second comma-separated field from each line. Straightforward field extraction.

---

### 2.
```
2024
2024
```
**Why:** `-c1-4` selects byte positions 1 through 4 from each line. Useful for fixed-width formats like dates. No delimiter needed.

---

### 3.
```
(three blank lines)
```
**Why:** This is the core `cut` trap. `cut -d' '` splits on a **single space character**. `"alice   90"` has multiple spaces, so field 2 is an empty string (the character between the 1st and 2nd space). `cut` does not collapse runs of spaces. Verified output is three empty lines.

---

### 4.
```
90
75
```
**Why:** awk's default field separator (`$FS`) matches **one or more whitespace characters** (spaces or tabs). So `$2` correctly skips the space padding and lands on `90`. This is why awk is preferred over `cut` for human-edited space-separated data. Contrast with exercise 3.

---

### 5.
```
bat cat dog
bat fish
```
**Why:** `sed 's/cat/bat/'` replaces only the **first** occurrence of `cat` per line. Line 1 has two `cat`s — only the first becomes `bat`. To replace all, use `s/cat/bat/g`.

---

### 6.
```
line1
line2
line3
line4
line5
line5
line6
```
**Why:** `sed '5p'` without `-n` still prints every line (default behaviour), AND the `p` command prints line 5 a second time — so line 5 appears twice. Always use `-n '5p'` when you want only the matched line.

---

### 7.
```
banana
cherry
```
**Why:** `/^a/d` deletes every line that starts with `a`. `apple` and `apricot` both match `^a` and are removed. `banana` and `cherry` pass through.

---

### 8.
```
1 3
2 2
3 4
```
**Why:** `NR` is the current line number; `NF` is the number of whitespace-separated fields on that line. Line 1 has 3 fields (`a b c`), line 2 has 2 (`d e`), line 3 has 4 (`f g h i`). This pattern is useful for spotting malformed rows in variable-width data.

---

### 9.
```
253
```
**Why:** `-F','` sets comma as field separator. `s+=$2` accumulates the second field (the score) across all lines. `END{print s}` fires after all input is consumed. `90+75+88 = 253`.

**How to test:** Swap out the numbers, recalculate manually, re-run.

---

### 10.
```
1 alice 95
3 carol 82
```
**Why:** `$3 > 70` is a pattern that filters lines where the third field exceeds 70. `bob` (60) and `dave` (45) are skipped. `NR` is the original line number — note it prints `1` and `3`, not `1` and `2`. The line number does not reset after filtering.

---

### 11.
`tail -n +2` output:
```
line2
line3
line4
```
`tail -n 2` would print:
```
line3
line4
```
**Why:** `+2` means "start output at line 2" — it skips the header. `2` (no `+`) means "the last 2 lines". These are opposite operations; confusing them silently corrupts pipelines.

---

### 12.
```
phn numbr: -
```
**Why:** `tr -d '0-9'` deletes every character that is a digit (0 through 9). The letters, spaces, colon, and hyphen are untouched. Notice `3` is deleted from `ph0n3` and `numb3r`, leaving `phn` and `numbr`.

---

### 13.
```
too many spaces
```
**Why:** `tr -s ' '` squeezes runs of repeated spaces into a single space. It does not strip leading/trailing spaces. It only works on the character you specify — it won't squeeze tabs unless you also include `'\t'`.

---

## Write exercises

### 14.
```bash
awk -F: '{print $1}' /etc/passwd | head -5
```
**Edge-case note:** Do not use `cut -d: -f1` if you want to handle any line quirks; either works here, but `awk -F:` is more composable. Test by piping through `wc -l` to confirm you get one name per line.

---

### 15.
```bash
sed -n '3,5p' data.txt
```
**Edge-case note:** `3,5p` is a line address range. If the file has fewer than 5 lines, sed prints what exists and stops — no error. Test with a 3-line file to verify you get exactly lines 3–3.

---

### 16.
```bash
awk '{s+=$1} END{print s}' numbers.txt
```
**Edge-case note:** If any line is blank or contains a non-numeric value in field 1, awk silently treats it as 0 — no error thrown. Test with an intentionally malformed line to confirm behaviour.

---

### 17.
```bash
echo "Hello World" | tr -d 'aeiouAEIOU'
```
**Edge-case note:** `tr` is character-class substitution, so listing characters in the set is correct. Verify: `echo "aeiou" | tr -d 'aeiouAEIOU'` should return an empty line.

---

### 18.
```bash
awk -F',' '$2 > 80 {print $1, $2}' scores.csv
```
**Edge-case note:** If `scores.csv` has a header row, it will pass the `> 80` test only if the header's second field looks numeric and large. Safer: `awk -F',' 'NR>1 && $2>80 {print $1, $2}'` to skip the header explicitly.

---

### 19.
```bash
grep 'ERROR' log.txt | wc -l
```
**Edge-case note:** `grep -c 'ERROR' log.txt` is a one-command alternative that counts matching lines directly. `wc -l` counts newlines, which works the same for non-empty output. Test with a file where `ERROR` appears twice on one line — both commands count it as 1 (they count lines, not occurrences).
