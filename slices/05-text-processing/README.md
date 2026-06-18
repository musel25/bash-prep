# Slice 5 — Text processing (cut, tr, sed, awk)

## Quick intro (cheat-sheet)

### cut
| Syntax | What it does |
|---|---|
| `cut -d',' -f2` | Split on comma, return field 2 |
| `cut -f1,3` | Fields 1 and 3, default delimiter is **TAB** |
| `cut -c1-4` | Characters 1 through 4 (byte positions) |

### tr
| Syntax | What it does |
|---|---|
| `tr 'a-z' 'A-Z'` | Translate lowercase → uppercase, char-by-char |
| `tr -d '0-9'` | Delete every digit |
| `tr -s ' '` | Squeeze runs of spaces into one space |

### head / tail / wc
| Syntax | What it does |
|---|---|
| `head -n 5` | First 5 lines |
| `tail -n 5` | Last 5 lines |
| `tail -n +2` | Skip line 1, print from line 2 onward (the `+` means "starting at") |
| `tail -f file` | Follow file live (log watching) |
| `wc -l` | Count lines |
| `wc -w` | Count words |
| `wc -c` | Count bytes |

### sed
| Syntax | What it does |
|---|---|
| `sed 's/old/new/'` | Replace **first** occurrence of `old` per line |
| `sed 's/old/new/g'` | Replace **all** occurrences per line |
| `sed -n '5p'` | Print only line 5 (silent mode suppresses others) |
| `sed '/regex/d'` | Delete lines matching regex |

### awk
| Syntax | What it does |
|---|---|
| `awk '{print $1}'` | Print first whitespace-delimited field |
| `awk '{print $NF}'` | Print **last** field (NF = number of fields on this line) |
| `awk -F','` | Set field separator to comma |
| `awk -F:` | Set field separator to colon |
| `NR` | Current record (line) number |
| `NF` | Number of fields on the current line |
| `awk '$3 > 10'` | Print lines where field 3 > 10 (pattern with no action = print) |
| `awk '{s+=$1} END{print s}'` | Accumulate field 1 into `s`, print after all lines |

---

## Classic gotchas

- **`cut` splits on literal single delimiter chars.** `cut -d' ' -f2` on `"alice   90"` returns empty — the second "field" is another space, not `90`. awk's default `$2` handles runs of whitespace correctly.
- **`sed 's/old/new/'` is NOT global.** Without `/g`, only the first match per line is replaced. Forgetting `/g` is the #1 sed mistake.
- **`sed '5p'` without `-n` prints every line AND line 5 twice.** Always pair `p` with `-n` when you only want the matched output.
- **`tail -n +2` vs `tail -n 2` are opposites.** `+2` means "start at line 2" (skip the header). `2` means "last 2 lines".
- **`tr` is character-by-character, not string-by-string.** `tr 'abc' 'xyz'` maps `a→x`, `b→y`, `c→z` — it does NOT replace the substring `"abc"` with `"xyz"`.

---

## Exercises

Try each before peeking at answers.md.

### Read — what does this do / print?

**1.**
```bash
printf "alice,eng,90\nbob,mkt,75\ncarol,eng,88\n" | cut -d',' -f2
```
What is printed?

---

**2.**
```bash
printf "2024-06-15\n2024-07-01\n" | cut -c1-4
```
What is printed?

---

**3.**
```bash
printf "alice   90\nbob     75\n" | cut -d' ' -f2
```
What is printed? (Think carefully before answering.)

---

**4.**
```bash
printf "alice   90\nbob     75\n" | awk '{print $2}'
```
What is printed? How does this differ from exercise 3?

---

**5.**
```bash
printf "cat cat dog\ncat fish\n" | sed 's/cat/bat/'
```
What is printed?

---

**6.**
```bash
printf "line1\nline2\nline3\nline4\nline5\nline6\n" | sed '5p'
```
What is printed, and why might it surprise you?

---

**7.**
```bash
printf "apple\nbanana\napricot\ncherry\n" | sed '/^a/d'
```
What is printed?

---

**8.**
```bash
printf "a b c\nd e\nf g h i\n" | awk '{print NR, NF}'
```
What is printed?

---

**9.**
```bash
printf "alice,90\nbob,75\ncarol,88\n" | awk -F',' '{s+=$2} END{print s}'
```
What is printed?

---

**10.**
```bash
printf "alice eng 95\nbob mkt 60\ncarol eng 82\ndave mkt 45\n" \
  | awk '$3 > 70 {print NR, $1, $3}'
```
What is printed?

---

**11.**
```bash
printf "header\nline2\nline3\nline4\n" | tail -n +2
```
What is printed? What would `tail -n 2` print instead?

---

**12.**
```bash
echo "ph0n3 numb3r: 555-1234" | tr -d '0-9'
```
What is printed?

---

**13.**
```bash
printf "too    many   spaces" | tr -s ' '
```
What is printed?

---

### Write — how would you …?

**14.** Extract the username column (field 1, colon-separated) from `/etc/passwd` for all lines. Show the first 5 results.

**15.** Print only lines 3 through 5 of a file `data.txt` using `sed`. (No `head`/`tail`.)

**16.** Sum all values in the first column of a space-separated file `numbers.txt` and print the total.

**17.** Remove all vowels (a, e, i, o, u — lower and upper) from a string using `tr`.

**18.** Given a CSV file `scores.csv` with columns `name,score`, print the name and score for every row where score is above 80.

**19.** Count how many lines in a file `log.txt` contain the word `ERROR`. (Use `grep` and `wc` together.)
