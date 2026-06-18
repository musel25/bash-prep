# Mock bank — Modal-style snippets

**How to use:** Cover the screen below each snippet. Read the code aloud. Explain what it does step by step, then hit edge cases, then say how you'd test or improve it. Time yourself — target 90 seconds per item before checking answers.

---

### 1. (easy)

```bash
ps aux | grep myapp | wc -l
```

What's the bug / why doesn't it behave as intended?

---

### 2. (med)

```bash
for f in $(ls); do
    cp "$f" /backup/
done
```

What's the bug / why doesn't it behave as intended?

---

### 3. (med)

**Version A**
```bash
ls /nonexistent 2>&1 > output.txt
```

**Version B**
```bash
ls /nonexistent > output.txt 2>&1
```

Which version is more correct/efficient, and why?

---

### 4. (easy)

```
-rwxr-xr-- 1 alice devs 4096 Jun 18 09:00 deploy.sh
```

You are logged in as `bob`, a member of the `devs` group. Can you execute `deploy.sh`? Can you read it?

What are the edge cases?

---

### 5. (med)

```bash
start=$(date +%s)
process_chunk 1 &
process_chunk 2 &
process_chunk 3 &
wait
end=$(date +%s)
echo "Done in $((end - start))s"
```

Each `process_chunk` call takes ~10 seconds alone. Explain what this does, step by step. What elapsed time do you expect, and what are the edge cases?

---

### 6. (easy)

```bash
cat access.log | sort | uniq -c | sort -nr | head -10
```

Explain what this does, step by step. How would you adapt it to find the top-10 most frequent IP addresses given that the IP is the first field on each line?

---

### 7. (med)

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head -5
```

Explain what this does, step by step. What are the edge cases?

---

### 8. (hard)

```bash
set -e

run_checks() {
    grep -q "ERROR" app.log
}

if run_checks; then
    echo "errors found"
fi

echo "script finished"
```

`app.log` contains no errors. What prints? What's the surprise?

---

### 9. (hard)

**Version A**
```bash
set -e
false | true
echo "still running"
```

**Version B**
```bash
set -e
set -o pipefail
false | true
echo "still running"
```

Which version is more correct/efficient, and why?

---

### 10. (med)

```bash
echo "root:x:0:0:root:/root:/bin/bash" | cut -d: -f7
echo "no-colons-here" | cut -d: -f2
```

Explain what this does, step by step. What are the edge cases?

---

### 11. (hard)

```bash
DIR=$1
rm -rf ${DIR}/cache
```

What's the bug / why doesn't it behave as intended?

---

### 12. (med)

**Version A**
```bash
kill $PID
```

**Version B**
```bash
kill -9 $PID
```

Which version is more correct/efficient, and why?

---

### 13. (med)

```bash
while IFS= read -r line; do
    count=$(echo "$line" | wc -c)
    total=$((total + count))
done < bigfile.txt
echo "Total bytes: $total"
```

Why is this loop slow? How would you fix it?

---

### 14. (med)

**Version A**
```bash
grep -c "ERROR" app.log
```

**Version B**
```bash
grep "ERROR" app.log | wc -l
```

Which version is more correct/efficient, and why?

---

### 15. (hard)

**Version A**
```bash
count=0
cat data.txt | while read line; do
    count=$((count + 1))
done
echo "Lines: $count"
```

**Version B**
```bash
count=0
while IFS= read -r line; do
    count=$((count + 1))
done < data.txt
echo "Lines: $count"
```

Which version is more correct/efficient, and why?

---

### 16. (med)

**Version A**
```bash
find . -name "*.log" -exec wc -l {} \;
```

**Version B**
```bash
find . -name "*.log" | xargs wc -l
```

Which version is more correct/efficient, and why?

---

### 17. (easy)

```bash
ls /nonexistent > output.txt 2>&1
echo "exit code: $?"
cat output.txt
```

Explain what this does, step by step. How would you test or validate this?

---

### 18. (hard)

```bash
LOG_DIR="/var/log/myapp"
find "$LOG_DIR" -name "*.tmp" -mtime +7 | xargs rm -f
```

What are the edge cases? How would you make this safer?
