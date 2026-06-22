#!/usr/bin/env python3
"""Build the 'Bash — Modal screen' Anki deck via AnkiConnect.

Run:  uv run --no-project python build_deck.py
Requires Anki running with the AnkiConnect add-on (localhost:8765).

Every output-prediction card whose answer matters is listed in VERIFY and is
re-run in real bash at build time; a mismatch aborts the push (evidence over
assertion — see CLAUDE.md learning contract).
"""
import html
import json
import subprocess
import sys
import urllib.request

DECK = "Bash — Modal screen"
MODEL = "Bash QA (modal-prep)"
ANKI = "http://localhost:8765"

# ── helpers ──────────────────────────────────────────────────────────────────
def pre(s: str) -> str:
    return ('<pre style="background:#f4f4f4;padding:6px 8px;border-radius:5px;'
            'white-space:pre-wrap">' + html.escape(s) + "</pre>")

cards = []
def C(tag, front, back):
    cards.append({"tag": tag, "front": front, "back": back})

def read_q(snippet, extra=""):
    return f"<b>What does this print?</b>{extra}" + pre(snippet)

def out_a(output, why):
    return "<b>Output:</b>" + pre(output) + why

# ── 1. PIPES & REDIRECTION (tag: pipes) ──────────────────────────────────────
C("pipes", read_q("ls /nonexistent | wc -l"),
  out_a("ls: cannot access '/nonexistent': No such file or directory\n0",
        "A pipe connects <b>stdout only</b>. The error goes to <b>stderr</b>, bypasses "
        "the pipe, and prints to the terminal. <code>wc -l</code> sees an empty stream → "
        "<b>0</b>."))

C("pipes", read_q("ls /nonexistent 2>&1 | wc -l"),
  out_a("1",
        "<code>2>&1</code> merges stderr into stdout <i>before</i> the pipe, so the "
        "one-line error now flows through the pipe and is counted → <b>1</b>."))

C("pipes", read_q("{ echo out; echo err >&2; } 2>&1 > capture.txt",
                  "<br>(terminal? file?)"),
  out_a("terminal shows: err\ncapture.txt contains: out",
        "<b>Ordering trap.</b> Left→right: <code>2>&1</code> copies fd1's <i>current</i> "
        "target (terminal) to fd2; <i>then</i> <code>&gt;capture.txt</code> moves fd1 to "
        "the file. stderr stays pinned to the terminal. Correct order: "
        "<code>&gt;capture.txt 2&gt;&amp;1</code>."))

C("pipes", "<b>Which is right to capture BOTH stdout+stderr to a file?</b>"
  + pre("A) cmd 2>&1 > out.txt\nB) cmd > out.txt 2>&1"),
  "<b>B.</b> Redirect stdout to the file first, then point stderr at where stdout now is. "
  "A leaves stderr on the terminal (out.txt gets only stdout). "
  "Mnemonic: <i>stdout first, then aim stderr at it.</i>")

C("pipes", read_q("false | true\necho \"exit: $?\"\necho \"PIPESTATUS: ${PIPESTATUS[@]}\""),
  out_a("exit: 0\nPIPESTATUS: 0",
        "<b>The real trap (verified).</b> <code>$?</code> is only the <b>last</b> stage "
        "(<code>true</code>→0). PIPESTATUS <i>would</i> be <code>1 0</code> — but the "
        "<code>echo \"exit…\"</code> ran first and <b>reset PIPESTATUS to its own status (0)</b>. "
        "You must read PIPESTATUS on the line <i>immediately</i> after the pipe."))

C("pipes", read_q("false | true\necho \"${PIPESTATUS[@]}\""),
  out_a("1 0",
        "Read immediately after the pipeline: index 0 = <code>false</code> (1), "
        "index 1 = <code>true</code> (0). Any command in between overwrites PIPESTATUS."))

C("pipes", "<b>$? vs ${PIPESTATUS[@]}?</b>",
  "<code>$?</code> = exit code of the <b>last</b> command only. In a pipeline it hides "
  "earlier failures (<code>generate | upload</code> can fail silently). "
  "<code>${PIPESTATUS[@]}</code> = per-stage codes — capture it the very next line.")

C("pipes", read_q("set -o pipefail\ngrep NOMATCH /etc/hostname | wc -l\necho \"exit: $?\""),
  out_a("0\nexit: 1",
        "<code>grep</code> finds nothing → exits 1. <code>wc</code> still prints 0 lines. "
        "With <code>pipefail</code> the pipeline's exit is the rightmost non-zero code → "
        "<b>1</b>. Without it, exit would be 0 and the failure invisible."))

C("pipes", read_q("echo -e \"a\\nb\\nc\" | tee /tmp/out.txt | wc -l", "<br>(terminal + file)"),
  out_a("terminal: 3\n/tmp/out.txt: a / b / c",
        "<code>tee</code> writes its stdin to <b>both</b> the file and its own stdout, so "
        "downstream <code>wc -l</code> still counts all 3 lines. Nothing is lost."))

C("pipes", "<b>Save only stderr to errors.log?</b>",
  pre("make build 2> errors.log") + "Only fd2 redirected; stdout still hits the terminal.")

C("pipes", "<b>Discard stdout AND stderr but keep the exit code?</b>",
  pre("curl https://example.com &> /dev/null\necho $?")
  + "<code>&amp;&gt;</code> = bash shorthand for <code>&gt;/dev/null 2&gt;&amp;1</code>. "
  "Redirection discards output but the exit code survives.")

C("pipes", "<b>The three standard streams + their fd numbers?</b>",
  "<b>0</b> = stdin (input) · <b>1</b> = stdout (normal output) · <b>2</b> = stderr "
  "(errors). A pipe <code>|</code> carries fd1 only; fd2 must be merged with "
  "<code>2&gt;&amp;1</code> to travel through it.")

C("pipes", "<b>> vs >> vs &lt; ?</b>",
  "<code>&gt;</code> overwrite (truncate) stdout to file · <code>&gt;&gt;</code> append · "
  "<code>&lt;</code> feed a file in as stdin.")

# ── 2. QUOTING & WORD-SPLITTING (tag: quoting) ───────────────────────────────
C("quoting", read_q("name=Alice\necho 'Hello $name'"),
  out_a("Hello $name",
        "Single quotes are fully literal — <b>no</b> expansion of any kind. <code>$name</code> "
        "prints verbatim."))

C("quoting", read_q("name=Alice\necho \"Hello $name\""),
  out_a("Hello Alice",
        "Double quotes allow <code>$var</code> expansion (but still protect spaces & globs)."))

C("quoting", read_q('x="hello  world"\necho $x\necho "---"\necho "$x"'),
  out_a("hello world\n---\nhello  world",
        "Unquoted <code>$x</code> is <b>word-split</b> on whitespace into 2 args; "
        "<code>echo</code> rejoins with single spaces → double space collapses. "
        "<code>\"$x\"</code> is one arg, spacing intact."))

C("quoting", read_q('file="my report.txt"\nwc -w $file'),
  out_a("wc: my: No such file or directory\nwc: report.txt: No such file or directory\n0 total",
        "Unquoted <code>$file</code> splits into <code>my</code> and <code>report.txt</code> — "
        "two nonexistent files. The canonical spaces-in-filename bug. Fix: "
        "<code>wc -w \"$file\"</code>. Same reason <code>rm $file</code> is dangerous."))

C("quoting", read_q('x="a b c"\n[ -z $x ] && echo empty || echo notempty'),
  out_a("bash: [: too many arguments\nnotempty",
        "Unquoted <code>$x</code> → <code>[ -z a b c ]</code> = too many args (exit 2). "
        "The <code>||</code> branch then runs. Fix: <code>[ -z \"$x\" ]</code>."))

C("quoting", read_q('f() { echo "count: $#"; for a in $@; do echo "[$a]"; done; }\n'
                    'f "hello world" foo'),
  out_a("count: 2\n[hello]\n[world]\n[foo]",
        "<code>$#</code>=2 (shell counted before the call). But unquoted <code>$@</code> "
        "word-splits <code>\"hello world\"</code> into two. Only <code>\"$@\"</code> "
        "preserves each original arg → <code>[hello world]</code> <code>[foo]</code>."))

C("quoting", "<b>\"$@\" vs \"$*\" ?</b>",
  "<code>\"$@\"</code> → each positional arg as its <b>own</b> quoted word (the correct "
  "way to forward args). <code>\"$*\"</code> → <b>all</b> args joined into ONE string "
  "(first char of IFS, default space). Unquoted <code>$@</code>/<code>$*</code> both "
  "word-split.")

C("quoting", read_q('echo *.xyz', "<br>(no matching files exist)"),
  out_a("*.xyz",
        "By default bash leaves an <b>unmatched glob literal</b> — it does NOT become empty "
        "and does NOT error. Scripts that assume 'no match = nothing' then operate on the "
        "string <code>*.xyz</code>. <code>shopt -s nullglob</code> makes it expand to empty."))

C("quoting", read_q('IFS=:\nx="a:b:c"\nfor w in $x; do echo "word: $w"; done'),
  out_a("word: a\nword: b\nword: c",
        "<code>IFS</code> controls split characters. Set to <code>:</code>, unquoted "
        "<code>$x</code> splits on colons. Quoting <code>\"$x\"</code> would suppress "
        "splitting (one iteration)."))

C("quoting", read_q('for f in $(ls); do echo "[$f]"; done',
                    "<br>(dir has 'hello world.txt')"),
  out_a("[hello]\n[world.txt]\n...",
        "<b>Never parse ls.</b> <code>$(ls)</code> word-splits 'hello world.txt' into two. "
        "Use a glob: <code>for f in *; do …</code> — the shell never splits inside a "
        "filename produced by globbing."))

C("quoting", "<b>Safely forward all script args to grep?</b>",
  pre('grep "$@"') + "<code>\"$@\"</code> is the only form that keeps each arg (incl. ones "
  "with spaces) intact as separate words.")

C("quoting", "<b>echo \"$HOME\" vs echo '$HOME' ?</b>",
  "Double quotes → expands to e.g. <code>/home/musel</code>. Single quotes → literal "
  "<code>$HOME</code>. Quote variables by default; prefer double quotes unless you "
  "explicitly want zero expansion.")

# ── 3. EXIT CODES & CONDITIONALS (tag: exit-codes) ───────────────────────────
C("exit-codes", read_q('ls /nonexistent\necho "ls exit=$?"\necho "echo exit=$?"'),
  out_a("ls exit=2\necho exit=0",
        "<code>ls</code> fails (2). First echo prints it but <b>also resets $? to 0</b> "
        "(echo succeeded), which the second echo reads. Capture immediately: "
        "<code>rc=$?</code>."))

C("exit-codes", read_q('true && echo yes && false && echo never\necho "exit=$?"'),
  out_a("yes\nexit=1",
        "<code>true</code>→0, <code>echo yes</code> runs, <code>false</code>→1 so "
        "<code>&amp;&amp;</code> short-circuits; <code>never</code> is skipped. "
        "<code>$?</code>=1 (last command that ran was <code>false</code>)."))

C("exit-codes", read_q('deploy && verify || echo ROLLBACK',
                       "<br>(deploy succeeds, verify FAILS)"),
  out_a("ROLLBACK",
        "<b>a &amp;&amp; b || c is NOT if/else.</b> deploy ok → verify runs → verify fails "
        "→ <code>||</code> fires ROLLBACK. The else-branch runs whenever <b>b</b> fails, "
        "not just <b>a</b>. Use real <code>if/then/else</code>."))

C("exit-codes", "<b>Why is `a && b || c` unsafe as if/else? Safe version?</b>",
  "If <b>b</b> itself fails, <b>c</b> also runs — false alarm. Only "
  "<code>if a; then b; else c; fi</code> is safe (c runs solely when a fails).")

C("exit-codes", read_q('name="John Smith"\n[ $name = "John Smith" ]\necho "exit=$?"'),
  out_a("bash: [: too many arguments\nexit=2",
        "Unquoted <code>$name</code> → <code>[ John Smith = … ]</code>, 3 words on the "
        "left. <code>[ ]</code> is a command and word-splits. Fix: quote, or use "
        "<code>[[ ]]</code>."))

C("exit-codes", read_q('name="John Smith"\n[[ $name = "John Smith" ]]\necho "exit=$?"'),
  out_a("exit=0",
        "<code>[[ ]]</code> is a bash <b>keyword</b>, not a command — it suppresses "
        "word-splitting on unquoted vars. Comparison succeeds."))

C("exit-codes", "<b>[ ] vs [[ ]] — three differences?</b>",
  "1) <code>[ ]</code> is a command (<code>test</code>); <code>[[ ]]</code> a keyword. "
  "2) <code>[[ ]]</code> doesn't word-split/glob unquoted vars. "
  "3) In <code>[[ ]]</code> <code>&lt; &gt;</code> compare strings safely; in "
  "<code>[ ]</code> they're <b>redirections</b> unless escaped.")

C("exit-codes", read_q('[ 10 -gt 9 ] && echo A\n[ "10" \\> "9" ] && echo B'),
  out_a("A",
        "<code>-gt</code> is numeric: 10&gt;9 → A. <code>\\&gt;</code> is <b>lexical</b> "
        "string compare: '1' &lt; '9' so \"10\" sorts before \"9\" → false, no B. "
        "(Unescaped <code>&gt;</code> would create a file named <code>9</code>.)"))

C("exit-codes", read_q('[ 0 ] && echo true || echo false'),
  out_a("true",
        "Single-arg <code>[ x ]</code> tests <b>non-empty string</b>. \"0\" is one char → "
        "true. In shell <code>[ ]</code> <b>every non-empty string is true</b> (unlike "
        "C/Python). To test zero: <code>[ \"$n\" -eq 0 ]</code>."))

C("exit-codes", "<b>-eq/-lt/-gt vs =/&lt;/&gt; in tests?</b>",
  "<code>-eq -ne -lt -le -gt -ge</code> = <b>numeric</b> comparison. "
  "<code>= != &lt; &gt;</code> = <b>string</b> (lexical) comparison. "
  "<code>[ \"10\" = \"10.0\" ]</code> is false; <code>[ 10 -eq 10 ]</code> with 10.0 errors.")

C("exit-codes", read_q('set -e\nif false; then echo a; fi\necho "after"'),
  out_a("after",
        "<code>set -e</code> does <b>not</b> abort on a command used as an "
        "<code>if</code> condition — failure there is 'handled'. Same exemption for "
        "<code>while</code>/<code>until</code>, <code>&amp;&amp;</code>/<code>||</code> "
        "operands, and <code>!</code>."))

C("exit-codes", "<b>set -euo pipefail — what does each do, and the -e exemptions?</b>",
  "<code>-e</code> abort on unchecked non-zero · <code>-u</code> abort on unset var · "
  "<code>-o pipefail</code> pipeline fails if any stage fails.<br>"
  "<b>-e exemptions:</b> <code>if</code>/<code>while</code> conditions, operands of "
  "<code>&amp;&amp; || !</code>, non-final pipeline stages. <code>${V:-x}</code> dodges "
  "<code>-u</code>.")

C("exit-codes", read_q('set -u\necho "${MISSING:-default}"\necho "exit=$?"'),
  out_a("default\nexit=0",
        "<code>:-</code> default-value expansion does NOT trip <code>set -u</code> — it "
        "substitutes the default. The safe idiom for optional vars. Plain "
        "<code>$MISSING</code> would abort."))

C("exit-codes", "<b>Common exit codes: 0, 1, 2, 126, 127, 130?</b>",
  "0 success · 1 generic failure (grep no-match) · 2 misuse / <code>[ ]</code> error · "
  "126 found-but-not-executable · 127 command not found · 130 killed by Ctrl+C (128+SIGINT 2).")

# ── 4. FIND & FILTER (tag: find-filter) ──────────────────────────────────────
C("find-filter", read_q('printf "8\\n10\\n9\\n100\\n2\\n" | sort'),
  out_a("10\n100\n2\n8\n9",
        "<code>sort</code> is <b>lexical by default</b>: compares char-by-char, so '10' &lt; "
        "'2'. Use <code>sort -n</code> for numeric → 2 8 9 10 100."))

C("find-filter", read_q('printf "apple\\nbanana\\napple\\nbanana\\nbanana\\napple\\n" | uniq -c'),
  out_a("      1 apple\n      1 banana\n      1 apple\n      2 banana\n      1 apple",
        "<code>uniq</code> collapses only <b>adjacent</b> dups. Unsorted input → 5 lines, "
        "not 2. Only the two adjacent bananas merge. <code>sort | uniq -c</code> gives "
        "true counts."))

C("find-filter", read_q('printf "python\\nbash\\npython\\ngo\\nbash\\npython\\n'
                        'rust\\ngo\\nbash\\npython\\n" | sort | uniq -c | sort -nr'),
  out_a("      4 python\n      3 bash\n      2 go\n      1 rust",
        "The classic <b>top-N idiom</b>: <code>sort</code> groups → <code>uniq -c</code> "
        "counts → <code>sort -nr</code> ranks high-to-low. Works for log levels, IPs, "
        "HTTP codes."))

C("find-filter", "<b>The frequency / top-N one-liner?</b>",
  pre("sort f | uniq -c | sort -nr | head") + "Group (sort), count (uniq -c), rank "
  "(sort -nr). The leading <code>sort</code> is mandatory — uniq only sees adjacency.")

C("find-filter", read_q('printf "c.t\\ncat\\ncot\\n" | grep "c.t"'),
  out_a("c.t\ncat\ncot",
        "In regex <code>.</code> = <b>any single char</b>, so all three match (and 'cbt' "
        "would too). For a literal dot: <code>grep 'c\\.t'</code> or <code>grep -F 'c.t'</code>."))

C("find-filter", read_q('find . -name "*.log" | xargs wc -l',
                        "<br>(a file is named 'my app.log')"),
  out_a("wc: ./my: No such file or directory\nwc: app.log: No such file or directory ...",
        "<code>xargs</code> splits input on <b>whitespace</b> → 'my app.log' becomes two "
        "args. Fix: <code>find … -print0 | xargs -0 wc -l</code> (null-delimited)."))

C("find-filter", "<b>find -exec {} \\; vs {} + ?</b>",
  "<code>\\;</code> runs the command <b>once per file</b> (N forks). <code>+</code> batches "
  "<b>many files per invocation</b> (like xargs) — far faster when startup is costly "
  "(gzip, rsync). Both pass filenames safely (no whitespace split).")

C("find-filter", "<b>Safely delete all *.tmp older than 7 days under $DIR?</b>",
  pre('find "$DIR" -name "*.tmp" -mtime +7 -delete')
  + "<code>-delete</code> avoids the pipe entirely (atomic per file, space-safe). "
  "Alt: <code>-print0 | xargs -0 rm</code>. <code>-mtime +7</code> = older than 7 days.")

C("find-filter", "<b>grep flags: -r -i -l -n -c -o -E -F ?</b>",
  "<code>-r</code> recurse · <code>-i</code> ignore case · <code>-l</code> filenames only · "
  "<code>-n</code> line numbers · <code>-c</code> count matches · <code>-o</code> only the "
  "match · <code>-E</code> extended regex · <code>-F</code> fixed (literal) string.")

C("find-filter", "<b>grep -c pat file  vs  grep pat file | wc -l — which is more correct?</b>",
  "<code>grep -c</code>. On a missing file it exits 2 and surfaces the error; the piped "
  "<code>wc -l</code> prints 0 and exits 0 — <b>the pipe swallows grep's failure</b>. "
  "Note <code>grep</code> exits 1 on zero matches → guard with <code>|| true</code> under "
  "<code>set -e</code>.")

C("find-filter", "<b>find: files modified in last 7 days AND bigger than 10 MB?</b>",
  pre("find . -type f -mtime -7 -size +10M")
  + "<code>-mtime -7</code> within 7 days · <code>-size +10M</code> &gt; 10 MB "
  "(units c/k/M/G). <code>-type f</code> excludes dirs.")

# ── 5. TEXT PROCESSING (tag: text) ───────────────────────────────────────────
C("text", read_q('echo "alice   90" | cut -d\' \' -f2'),
  out_a("(empty line)",
        "<b>cut trap.</b> <code>-d' '</code> splits on a <b>single</b> space and does NOT "
        "collapse runs. Field 2 is the empty bit between the 1st and 2nd space. Use "
        "<code>awk</code> for padded columns."))

C("text", read_q('echo "alice   90" | awk \'{print $2}\''),
  out_a("90",
        "awk's default field separator is <b>one or more</b> whitespace chars, so it skips "
        "the padding and lands on 90. Preferred over <code>cut</code> for "
        "human-spaced data."))

C("text", read_q('echo "no-colons-here" | cut -d: -f2'),
  out_a("no-colons-here",
        "When the delimiter is <b>absent</b>, <code>cut</code> prints the <b>whole line</b> "
        "(not empty) — a silent failure. <code>awk -F: '{print $2}'</code> returns empty, "
        "safer for scripts."))

C("text", read_q('echo "cat cat dog" | sed \'s/cat/bat/\''),
  out_a("bat cat dog",
        "<code>s/old/new/</code> replaces only the <b>first</b> match per line. Add "
        "<code>g</code> (<code>s/cat/bat/g</code>) to replace all."))

C("text", read_q('printf "l1\\nl2\\nl3\\n" | sed \'2p\''),
  out_a("l1\nl2\nl2\nl3",
        "Without <code>-n</code>, sed prints every line by default AND the <code>p</code> "
        "command prints line 2 again → it appears twice. Use <code>sed -n '2p'</code> for "
        "just that line."))

C("text", read_q('printf "a b c\\nd e\\nf g h i\\n" | awk \'{print NR, NF}\''),
  out_a("1 3\n2 2\n3 4",
        "<code>NR</code> = current line number, <code>NF</code> = field count on that line. "
        "Handy for spotting malformed rows in variable-width data."))

C("text", read_q('printf "a,90\\nb,75\\nc,88\\n" | awk -F\',\' \'{s+=$2} END{print s}\''),
  out_a("253",
        "<code>-F','</code> sets comma separator; <code>s+=$2</code> accumulates field 2; "
        "<code>END{}</code> fires after all input. 90+75+88=253."))

C("text", "<b>tail -n +2 f  vs  tail -n 2 f ?</b>",
  "<code>+2</code> = start output <b>at line 2</b> (skip the header). <code>2</code> = the "
  "<b>last 2</b> lines. Opposite operations — mixing them silently corrupts pipelines.")

C("text", read_q('echo "ph0n3 numb3r: 555-1234" | tr -d \'0-9\''),
  out_a("phn numbr: -",
        "<code>tr -d '0-9'</code> deletes every digit. Letters, spaces, colon, hyphen "
        "stay. <code>tr 'a-z' 'A-Z'</code> would translate instead of delete."))

C("text", "<b>Print only lines 3–5 of a file?</b>",
  pre("sed -n '3,5p' file") + "<code>-n</code> suppresses default printing; <code>3,5p</code> "
  "is a line-address range. Fewer than 5 lines → prints what exists, no error.")

# ── 6. PERMISSIONS, PROCESSES & CONCURRENCY (tag: perms-proc) ─────────────────
C("perms-proc", "<b>Read this mode: -rwxr-xr--</b>",
  "<code>-</code> regular file · owner <code>rwx</code> (read/write/execute) · group "
  "<code>r-x</code> (read/execute, no write) · other <code>r--</code> (read only). "
  "Octal = <b>754</b>.")

C("perms-proc", "<b>Octal: r/w/x values, and what are 755, 644, 751?</b>",
  "<code>r=4 w=2 x=1</code>, summed per class. <b>755</b>=rwxr-xr-x · <b>644</b>=rw-r--r-- · "
  "<b>751</b>=rwx--x--x (owner full, group/other execute-only).")

C("perms-proc", "<b>Mode 751 on script.sh — can a group member `cat` it? Run it?</b>",
  "Group bits are <code>--x</code> = <b>execute only</b>. They <b>can run</b> it (kernel "
  "reads it for them) but <b>cannot</b> <code>cat</code>/read the source — "
  "<code>Permission denied</code>. Execute is independent of read.")

C("perms-proc", "<b>On a DIRECTORY, what do r / w / x mean?</b>",
  "<code>r</code> = list names (<code>ls</code>) · <code>w</code> = create/delete/rename "
  "entries inside · <code>x</code> = <b>traverse</b> (<code>cd</code>, access anything "
  "inside). <code>r</code> without <code>x</code> is near-useless: you see names but can't "
  "<code>stat</code>/<code>cat</code>/enter (metadata shows as <code>?</code>).")

C("perms-proc", "<b>You're owner AND in the group. Which permission bits apply?</b>",
  "<b>Owner bits only</b> — first matching class wins (owner → group → other). Group bits "
  "do NOT add to owner bits. So an owner with <code>r--</code> can't write even if group "
  "is <code>rw-</code>.")

C("perms-proc", "<b>chmod 755 deploy.sh — why over chmod +x?</b>",
  "755 sets the full mode explicitly (owner rwx, group/other r-x). <code>chmod +x</code> "
  "only adds execute and may <b>leave stray write bits</b> from the umask. Verify with "
  "<code>ls -l</code> that group/other have no <code>w</code>.")

C("perms-proc", "<b>kill PID vs kill -9 PID — signal, catchable?</b>",
  "<code>kill</code> → <b>SIGTERM (15)</b>: polite, the process CAN catch it (trap), clean "
  "up, then exit — or ignore it. <code>kill -9</code> → <b>SIGKILL (9)</b>: immediate, "
  "CANNOT be caught/blocked/ignored, no cleanup runs.")

C("perms-proc", "<b>Correct way to stop a process (not straight to -9)?</b>",
  pre("kill PID\nsleep 5\nkill -0 PID 2>/dev/null && kill -9 PID")
  + "SIGTERM first (lets it flush buffers, release locks), then escalate to SIGKILL. "
  "<code>kill -0</code> sends no signal — just tests if the process still exists.")

C("perms-proc", read_q("time { sleep 2 & sleep 2 & sleep 2 & wait; }",
                       "<br>(roughly how long?)"),
  out_a("~2 seconds (not 6)",
        "<code>&amp;</code> backgrounds all three; they run <b>concurrently</b>; "
        "<code>wait</code> blocks for all. Wall-clock ≈ the <b>slowest</b> job, not the "
        "sum. This is why you parallelize I/O-bound work."))

C("perms-proc", "<b>$! and a bare `wait`?</b>",
  "<code>$!</code> = PID of the <b>most recently</b> backgrounded job (overwritten by the "
  "next <code>&amp;</code>). Bare <code>wait</code> blocks until <b>all</b> children "
  "finish; <code>wait $PID</code> waits for one; <code>wait -n</code> for the first to end.")

C("perms-proc", "<b>Run ≤8 downloads concurrently from urls.txt?</b>",
  pre("xargs -P8 -I{} curl -O {} < urls.txt")
  + "<code>-P8</code> = up to 8 parallel processes; as each finishes the next starts. "
  "<code>-P0</code> = unlimited (careful). Bounds concurrency vs forking thousands.")

C("perms-proc", "<b>Why is `for f in *.txt; do grep x \"$f\"; done` slower than "
  "`grep x *.txt`?</b>",
  "Every external command = a <b>fork+exec</b> (~ms). The loop spawns one "
  "<code>grep</code> <b>per file</b> (N processes); the single <code>grep</code> opens all "
  "files internally (1 process). Gap explodes with scale (~600× on 1000 items). General "
  "rule: let one tool process the whole input.")

C("perms-proc", "<b>Count running 'myapp' processes — what's wrong with "
  "`ps aux | grep myapp | wc -l`?</b>",
  "The <code>grep myapp</code> process itself contains 'myapp' → count inflated by ≥1 "
  "(can never return 0). Fixes: <code>pgrep -c myapp</code> (cleanest), "
  "<code>grep -v grep</code>, or the bracket trick <code>grep '[m]yapp'</code>.")

# ── 7. VARIABLES & SCRIPTING (tag: scripting) ────────────────────────────────
C("scripting", read_q('name = Alice\necho "Hello, $name"'),
  out_a("bash: name: command not found\nHello,",
        "<b>No spaces around =.</b> <code>name = Alice</code> runs a command "
        "<code>name</code> with args <code>=</code> and <code>Alice</code>. Assignment "
        "never happens → <code>$name</code> is empty. Correct: <code>name=Alice</code>."))

C("scripting", "<b>\"$*\" vs \"$@\" called as  script \"hello world\" foo bar ?</b>",
  "<code>\"$*\"</code> → one blob: <code>hello world foo bar</code> (one loop iteration). "
  "<code>\"$@\"</code> → three words: <code>hello world</code> / <code>foo</code> / "
  "<code>bar</code>. With spaced filenames, <code>\"$*\"</code> is almost always wrong.")

C("scripting", read_q('f="archive.tar.gz"\necho "${f##*.}"\necho "${f%.*}"\necho "${f%%.*}"'),
  out_a("gz\narchive.tar\narchive",
        "<code>##*.</code> strip <b>longest</b> prefix to a dot → extension <code>gz</code>. "
        "<code>%.*</code> strip <b>shortest</b> suffix from end → drop <code>.gz</code>. "
        "<code>%%.*</code> strip <b>longest</b> suffix → <code>archive</code>. "
        "(<code>#</code>=front, <code>%</code>=back; doubled=greedy.)"))

C("scripting", "<b>Parameter expansion: ${#f}, ${f:-d}, ${f:?msg} ?</b>",
  "<code>${#f}</code> = length · <code>${f:-d}</code> = use <b>d</b> if f unset/empty "
  "(doesn't trip <code>set -u</code>) · <code>${f:?msg}</code> = abort with msg if "
  "unset/empty (a good guard before <code>rm -rf</code>).")

C("scripting", read_q('printf "foo\\\\bar\\n" | { read line; echo "$line"; }',
                      "<br>(read WITHOUT -r)"),
  out_a("foobar",
        "Without <code>-r</code>, <code>read</code> treats <code>\\</code> as an escape and "
        "eats it → <code>foobar</code>. <code>read -r</code> keeps it literal "
        "(<code>foo\\bar</code>). Always use <code>read -r</code>."))

C("scripting", "<b>Why use `local` inside a function?</b>",
  "Without <code>local</code>, an assignment modifies the <b>global</b> of the same name — "
  "silently clobbering a caller's variable. <code>local x=…</code> confines it to the "
  "function's scope.")

C("scripting", read_q('count=0\necho -e "a\\nb\\nc" | while read l; do count=$((count+1)); done\n'
                      'echo "count=$count"'),
  out_a("count=0",
        "<b>Subshell trap.</b> The right side of a pipe runs in a <b>subshell</b>; "
        "<code>count</code> changes there are lost. Fix: redirect instead — "
        "<code>while read … done &lt; file</code> or <code>&lt; &lt;(cmd)</code> — so the "
        "loop runs in the current shell."))

C("scripting", "<b>bash script.sh  vs  ./script.sh — permission & shebang?</b>",
  "<code>bash script.sh</code>: bash reads the file → needs only <b>read</b>, ignores the "
  "shebang. <code>./script.sh</code>: the OS executes it → needs the <b>execute bit</b> "
  "(<code>chmod +x</code>) AND a valid shebang, and the file must be on the path you give "
  "(cwd isn't in <code>$PATH</code>).")

C("scripting", "<b>What does #!/usr/bin/env bash do, vs #!/bin/bash ?</b>",
  "The shebang tells the kernel which interpreter to run the file with when executed "
  "directly. <code>/usr/bin/env bash</code> finds bash via <code>$PATH</code> — "
  "<b>portable</b> across systems where bash isn't at <code>/bin/bash</code>.")

C("scripting", "<b>Read a file line-by-line, robustly?</b>",
  pre('while IFS= read -r line; do\n  echo "$line"\ndone < file')
  + "<code>IFS=</code> keeps leading/trailing whitespace; <code>-r</code> keeps "
  "backslashes; <code>&lt; file</code> (not <code>cat | while</code>) keeps the loop in "
  "the current shell.")

# ── verification battery (run in real bash; abort on mismatch) ────────────────
def run(snippet):
    r = subprocess.run(["bash", "-c", snippet], capture_output=True, text=True)
    out = (r.stdout + r.stderr)
    return "\n".join(line.rstrip() for line in out.splitlines()).strip()

def norm(s):  # collapse internal whitespace runs (for uniq -c padding)
    return "\n".join(" ".join(line.split()) for line in s.splitlines())

VERIFY = [
    ("eq",  'false | true; echo "${PIPESTATUS[@]}"', "1 0"),
    ("eq",  'false | true; echo "exit: $?"; echo "PIPESTATUS: ${PIPESTATUS[@]}"',
            "exit: 0\nPIPESTATUS: 0"),
    ("eq",  'x="hello  world"; echo $x; echo "---"; echo "$x"',
            "hello world\n---\nhello  world"),
    ("eq",  'printf "8\\n10\\n9\\n100\\n2\\n" | sort', "10\n100\n2\n8\n9"),
    ("eq",  'printf "8\\n10\\n9\\n100\\n2\\n" | sort -n', "2\n8\n9\n10\n100"),
    ("eqnorm", 'printf "apple\\nbanana\\napple\\nbanana\\nbanana\\napple\\n" | uniq -c',
            "1 apple\n1 banana\n1 apple\n2 banana\n1 apple"),
    ("eqnorm", 'printf "python\\nbash\\npython\\ngo\\nbash\\npython\\nrust\\ngo\\nbash\\npython\\n"'
            ' | sort | uniq -c | sort -nr', "4 python\n3 bash\n2 go\n1 rust"),
    ("eq",  'echo "alice   90" | awk \'{print $2}\'', "90"),
    ("eq",  'echo "no-colons-here" | cut -d: -f2', "no-colons-here"),
    ("eq",  'echo "cat cat dog" | sed \'s/cat/bat/\'', "bat cat dog"),
    ("eq",  'printf "l1\\nl2\\nl3\\n" | sed \'2p\'', "l1\nl2\nl2\nl3"),
    ("eq",  'printf "a b c\\nd e\\nf g h i\\n" | awk \'{print NR, NF}\'', "1 3\n2 2\n3 4"),
    ("eq",  'printf "a,90\\nb,75\\nc,88\\n" | awk -F\',\' \'{s+=$2} END{print s}\'', "253"),
    ("eq",  'echo "ph0n3 numb3r: 555-1234" | tr -d \'0-9\'', "phn numbr: -"),
    ("eq",  'f="archive.tar.gz"; echo "${f##*.}"; echo "${f%.*}"; echo "${f%%.*}"',
            "gz\narchive.tar\narchive"),
    ("eq",  'name="John Smith"; [[ $name = "John Smith" ]]; echo "exit=$?"', "exit=0"),
    ("eq",  '[ 0 ] && echo true || echo false', "true"),
    ("eq",  'set -u; echo "${MISSING:-default}"; echo "exit=$?"', "default\nexit=0"),
    ("eq",  'set -e; if false; then echo a; fi; echo after', "after"),
    ("eq",  'true && echo yes && false && echo never; echo "exit=$?"', "yes\nexit=1"),
    ("eq",  'name=Alice; echo "Hello, $name"', "Hello, Alice"),
    ("eq",  'count=0; echo -e "a\\nb\\nc" | while read l; do count=$((count+1)); done;'
            ' echo "count=$count"', "count=0"),
    ("contains", 'name="John Smith"; [ $name = "John Smith" ]; echo "exit=$?"',
                 "too many arguments"),
    ("contains", 'name="John Smith"; [ $name = "John Smith" ]; echo "exit=$?"', "exit=2"),
    ("contains", 'echo "alice   90" | cut -d\' \' -f2 | cat -A', "$"),  # empty field → "$"
]

def verify():
    fails = []
    for mode, snip, expect in VERIFY:
        got = run(snip)
        if mode == "eq":
            ok = got == expect
        elif mode == "eqnorm":
            ok = norm(got) == norm(expect)
        else:  # contains
            ok = expect in got
        if not ok:
            fails.append((snip, expect, got))
    if fails:
        print("VERIFICATION FAILED — not pushing:\n")
        for snip, exp, got in fails:
            print(f"  $ {snip}\n    expected: {exp!r}\n    got:      {got!r}\n")
        sys.exit(1)
    print(f"✓ verified {len(VERIFY)} snippets in real bash")

# ── AnkiConnect ──────────────────────────────────────────────────────────────
def anki(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKI, payload, {"Content-Type": "application/json"})
    res = json.load(urllib.request.urlopen(req, timeout=15))
    if res.get("error"):
        raise RuntimeError(f"{action}: {res['error']}")
    return res["result"]

def ensure_model():
    if MODEL in anki("modelNames"):
        return
    anki("createModel", modelName=MODEL,
         inOrderFields=["Front", "Back"],
         css=(".card{font-family:-apple-system,Segoe UI,sans-serif;font-size:17px;"
              "color:#222;background:#fff;text-align:left;max-width:640px;margin:0 auto;"
              "padding:14px} code{background:#eee;padding:1px 4px;border-radius:3px} "
              "hr#answer{border:none;border-top:1px solid #ccc;margin:12px 0}"),
         cardTemplates=[{
             "Name": "Reading drill",
             "Front": "{{Front}}",
             "Back": "{{FrontSide}}<hr id=answer>{{Back}}",
         }])
    print(f"✓ created note type {MODEL!r}")

def push():
    anki("createDeck", deck=DECK)
    ensure_model()
    notes = [{
        "deckName": DECK, "modelName": MODEL,
        "fields": {"Front": c["front"], "Back": c["back"]},
        "tags": ["bash-prep", c["tag"]],
        "options": {"allowDuplicate": False, "duplicateScope": "deck"},
    } for c in cards]
    can = anki("canAddNotes", notes=notes)
    ids = anki("addNotes", notes=notes)
    added = sum(1 for i in ids if i)
    skipped = len(ids) - added
    from collections import Counter
    by_tag = Counter(c["tag"] for c in cards)
    print(f"\nDeck: {DECK}")
    print(f"Added: {added}   Skipped (dupes/existing): {skipped}   Total cards in script: {len(cards)}")
    print("By tag: " + ", ".join(f"{t}={n}" for t, n in sorted(by_tag.items())))

if __name__ == "__main__":
    verify()
    push()
