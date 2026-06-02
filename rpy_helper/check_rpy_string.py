from pathlib import Path
import re

project_dir = Path(r"C:\Codes\RPY\VN_DGS\game")

SKIP_DIRS = {"tl", "cache", "saves"}

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
STRING_RE = re.compile(r'(?P<quote>["\'])(?P<text>.*?)(?P=quote)')


CHECK_LINE_RE = re.compile(
    r"""^\s*(
        text\b|
        textbutton\b|
        label\b|
        tooltip\b|
        imagebutton\b|
        button\b|
        frame\b|
        window\b|
        show\s+screen\b|
        call\s+screen\b|
        use\b|
        \$|
        default\b|
        define\b|
        python:
    )""",
    re.VERBOSE,
)

DIALOGUE_LINE_RE = re.compile(
    r"""^\s*(
        "[^"]*"|                
        '[^']*'|                
        \w+\s+"[^"]*"|           
        \w+\s+'[^']*'|           
        menu\s*:|
        translate\b|
        old\s+"[^"]*"|
        new\s+"[^"]*"
    )""",
    re.VERBOSE,
)

def is_wrapped_by_underscore(line: str, string_start: int) -> bool:
    before = line[:string_start].rstrip()
    return before.endswith("_(") or before.endswith("__(")

for rpy_file in project_dir.rglob("*.rpy"):
    if any(part in SKIP_DIRS for part in rpy_file.parts):
        continue

    with rpy_file.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            stripped = line.strip()

            if not stripped or stripped.startswith("#"):
                continue

            if not CJK_RE.search(line):
                continue

            # no normal scripts
            if DIALOGUE_LINE_RE.match(line):
                continue

            # check possible UI / screen / python lines
            if not CHECK_LINE_RE.match(line):
                continue

            for match in STRING_RE.finditer(line):
                text = match.group("text")

                if not CJK_RE.search(text):
                    continue

                if is_wrapped_by_underscore(line, match.start()):
                    continue

                print(f"{rpy_file}:{line_no}: possible untranslated UI string")
                print(f"    {line.rstrip()}")
                break