#!/usr/bin/env python3
"""Count story text in Ren'Py .rpy files.

Only dialogue/narration (say statements) and menu captions inside label blocks
are counted. The report is grouped by directory, file, and label.
"""

from __future__ import annotations

import ast
import csv
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

# ======================== 设置 ========================
# 剧本根目录。相对路径以本脚本所在目录为起点；也可以填写完整绝对路径。
SCRIPT_DIRECTORY = Path(r"C:\Codes\RPY\VN_HerWitch\game\scripts")

# Character 定义文件。相对路径以本脚本所在目录为起点。
# 设为 None，或者把 COUNT_CHARACTER_NAMES 设为 False，即可关闭角色名计数。
CHARACTER_FILE = Path(r"C:\Codes\RPY\VN_HerWitch\game\char.rpy")
COUNT_CHARACTER_NAMES = True

# CSV 输出位置。设为 None 就只在窗口/终端显示，不生成 CSV。相对路径同样以本脚本所在目录为起点。
CSV_OUTPUT = Path(r"script_stats.csv")
CSV_OUTPUT = None

# "characters"：去掉 Ren'Py tag 后，string 中每个字符都算 1 字，包括中英文标点和空格（推荐）。
# "han-words"：只算汉字、英文单词和数字，不含标点与空格。
COUNT_MODE = "characters"
# ================================================================

LABEL_RE = re.compile(r"^\s*label\s+([A-Za-z_][\w.]*)\s*(?:\([^:]*\))?\s*:\s*(?:#.*)?$")
BLOCK_RE = re.compile(r"^(?:init\s+)?python(?:\s+early)?\s*:\s*(?:#.*)?$")
MENU_RE = re.compile(r"^menu(?:\s+[^:]*)?\s*:\s*(?:#.*)?$")
IDENT_PREFIX_RE = re.compile(
    r"^[A-Za-z_]\w*(?:\s+(?:@\s*)?[A-Za-z_]\w*)*\s*$"
)

# A line beginning with one of these is a Ren'Py command, not a speaker name.
NON_SPEAKER_KEYWORDS = {
    "add", "audio", "bar", "button", "call", "camera", "choice", "default",
    "define", "drag", "fixed", "frame", "grid", "hide", "hotspot", "if",
    "image", "imagemap", "input", "jump", "key", "label", "menu", "mousearea",
    "music", "null", "onlayer", "pause", "play", "python", "queue", "return",
    "scene", "screen", "show", "side", "stop", "style", "text", "textbutton",
    "timer", "transform", "translate", "use", "vbar", "voice", "viewport",
    "vpgrid", "window", "with", "while", "zorder",
}

TEXT_TAG_RE = re.compile(r"\{(?:/?[A-Za-z][^{}]*|#|clear)\}")
INTERPOLATION_RE = re.compile(r"\[[^\[\]\n]+\]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
WORD_OR_NUMBER_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*|\d+(?:[.,]\d+)*")


@dataclass
class LabelStats:
    name: str
    text_count: int = 0
    name_count: int = 0
    say_count: int = 0
    menu_count: int = 0

    @property
    def count(self) -> int:
        return self.text_count + self.name_count

@dataclass
class FileStats:
    path: Path
    labels: list[LabelStats] = field(default_factory=list)

    @property
    def count(self) -> int:
        return sum(x.count for x in self.labels)

    @property
    def say_count(self) -> int:
        return sum(x.say_count for x in self.labels)

    @property
    def menu_count(self) -> int:
        return sum(x.menu_count for x in self.labels)

    @property
    def text_count(self) -> int:
        return sum(x.text_count for x in self.labels)

    @property
    def name_count(self) -> int:
        return sum(x.name_count for x in self.labels)


def indent_width(line: str) -> int:
    """Return indentation width, treating one tab as 8 columns."""
    prefix = line[: len(line) - len(line.lstrip(" \t"))]
    return len(prefix.expandtabs(8))


def strip_comment(line: str) -> str:
    """Remove a Ren'Py comment while preserving # characters inside strings."""
    quote = None
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
        elif ch == "\\" and quote:
            escaped = True
        elif quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#":
            return line[:i]
    return line


def quoted_literals(line: str) -> list[tuple[int, int, str]]:
    """Return (start, end, decoded value) for ordinary quoted literals."""
    found: list[tuple[int, int, str]] = []
    i = 0
    while i < len(line):
        if line[i] not in "\"'":
            i += 1
            continue
        quote = line[i]
        start = i
        i += 1
        escaped = False
        while i < len(line):
            ch = line[i]
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                raw = line[start : i + 1]
                try:
                    value = ast.literal_eval(raw)
                except (SyntaxError, ValueError):
                    value = raw[1:-1]
                found.append((start, i + 1, value))
                i += 1
                break
            i += 1
        else:
            break
    return found


def clean_text(text: str) -> str:
    """Remove Ren'Py formatting tags and dynamic interpolation expressions."""
    text = TEXT_TAG_RE.sub("", text)
    return INTERPOLATION_RE.sub("", text)


def count_text(text: str, mode: str) -> int:
    text = clean_text(text)
    if mode == "characters":
        # Literal string length: Chinese/English punctuation and spaces count.
        return len(text)
    # Chinese characters + English words + number groups; punctuation excluded.
    return len(HAN_RE.findall(text)) + len(WORD_OR_NUMBER_RE.findall(text))


def character_call_name(arguments: str) -> str | None:
    """Read the first static Character(...) argument without evaluating code."""
    try:
        expression = ast.parse(f"f({arguments})", mode="eval").body
    except SyntaxError:
        return None
    if not isinstance(expression, ast.Call) or not expression.args:
        return None
    first = expression.args[0]
    if isinstance(first, ast.Constant):
        return first.value if isinstance(first.value, str) else None
    # Also accept the common translation wrapper Character(_("Name"), ...).
    if (
        isinstance(first, ast.Call)
        and isinstance(first.func, ast.Name)
        and first.func.id == "_"
        and first.args
        and isinstance(first.args[0], ast.Constant)
        and isinstance(first.args[0].value, str)
    ):
        return first.args[0].value
    return None


def matching_parenthesis(text: str, open_index: int) -> int | None:
    """Find Character( ... )'s closing parenthesis, ignoring strings/comments."""
    depth = 0
    quote: str | None = None
    triple = False
    escaped = False
    in_comment = False
    i = open_index
    while i < len(text):
        ch = text[i]
        if in_comment:
            if ch == "\n":
                in_comment = False
            i += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif triple and text.startswith(quote * 3, i):
                quote = None
                triple = False
                i += 3
                continue
            elif not triple and ch == quote:
                quote = None
            i += 1
            continue
        if ch == "#":
            in_comment = True
        elif ch in "\"'":
            quote = ch
            triple = text.startswith(ch * 3, i)
            if triple:
                i += 3
                continue
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return None


def load_character_names(path: Path) -> dict[str, str]:
    """Parse `define tag = Character(static_name, ...)` definitions."""
    try:
        source = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Character 定义文件不是 UTF-8：{path}") from exc
    definitions: dict[str, str] = {}
    pattern = re.compile(
        r"(?m)^\s*(?:define\s+)?([A-Za-z_]\w*)\s*=\s*Character\s*\("
    )
    for match in pattern.finditer(source):
        open_index = match.end() - 1
        close_index = matching_parenthesis(source, open_index)
        if close_index is None:
            continue
        name = character_call_name(source[open_index + 1 : close_index])
        # Character(None, ...) and dynamic/non-literal names are intentionally skipped.
        if name is not None:
            definitions[match.group(1)] = name
    return definitions


def is_menu_caption(code: str, literal: tuple[int, int, str], menu_indents: list[int]) -> bool:
    if not menu_indents:
        return False
    start, end, _ = literal
    if code[:start].strip():
        return False
    suffix = code[end:].strip()
    # "Choice": or "Choice" if condition:
    return bool(re.fullmatch(r"(?:if\s+.+)?\s*:", suffix))


def say_text(code: str, literals: list[tuple[int, int, str]]) -> tuple[str, str | None] | None:
    """Recognize a say statement and return (spoken text, speaker tag)."""
    if not literals:
        return None
    first = literals[0]
    prefix = code[: first[0]].strip()
    suffix = code[first[1] :].strip()

    # Narration: "Text" (with optional say arguments after it).
    if not prefix:
        return first[2], None

    # Character speech: eileen happy "Text", extend "Text", centered "Text".
    if not IDENT_PREFIX_RE.fullmatch(prefix):
        return None
    first_word = prefix.split()[0]
    if first_word in NON_SPEAKER_KEYWORDS:
        return None

    # After dialogue Ren'Py permits arguments such as (what_color="#fff") and
    # a `with` clause. We intentionally ignore any later strings in that suffix.
    if suffix and not (suffix.startswith("(") or suffix.startswith("with ")):
        return None
    return first[2], first_word


def parse_file(path: Path, mode: str, character_names: dict[str, str]) -> FileStats:
    result = FileStats(path=path)
    current: LabelStats | None = None
    label_indent = -1
    python_indents: list[int] = []
    menu_indents: list[int] = []

    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError(f"不是 UTF-8 文件：{path}") from exc

    for raw_line in lines:
        code = strip_comment(raw_line).rstrip()
        stripped = code.strip()
        if not stripped:
            continue
        indent = indent_width(raw_line)

        label_match = LABEL_RE.match(code)
        if label_match:
            current = LabelStats(label_match.group(1))
            result.labels.append(current)
            label_indent = indent
            python_indents.clear()
            menu_indents.clear()
            continue

        if current is None:
            continue

        # A non-indented statement at or above the label level ends its body.
        if indent <= label_indent:
            current = None
            python_indents.clear()
            menu_indents.clear()
            continue

        python_indents[:] = [x for x in python_indents if indent > x]
        menu_indents[:] = [x for x in menu_indents if indent > x]

        if BLOCK_RE.match(stripped):
            python_indents.append(indent)
            continue
        if python_indents or stripped.startswith("$"):
            continue

        if MENU_RE.match(stripped):
            menu_indents.append(indent)
            continue

        literals = quoted_literals(code)
        if not literals:
            continue

        if is_menu_caption(code, literals[0], menu_indents):
            text = literals[0][2]
            current.text_count += count_text(text, mode)
            current.menu_count += 1
            continue

        say = say_text(code, literals)
        if say is not None:
            text, speaker_tag = say
            current.text_count += count_text(text, mode)
            if speaker_tag in character_names:
                current.name_count += count_text(character_names[speaker_tag], mode)
            current.say_count += 1

    return result


def relative_display(path: Path) -> str:
    return path.as_posix() if path.as_posix() != "." else "（根目录）"


def directory_totals(files: Iterable[FileStats], root: Path) -> dict[Path, int]:
    totals: dict[Path, int] = defaultdict(int)
    for item in files:
        relative_parent = item.path.relative_to(root).parent
        # Add to every real ancestor directory, excluding the scan root itself.
        current = relative_parent
        while current != Path("."):
            totals[current] += item.count
            current = current.parent
    return dict(totals)


def print_report(files: list[FileStats], root: Path, mode: str) -> None:
    total = sum(x.count for x in files)
    unit_note = "string 字符数（含中英文标点和空格，不含 Ren'Py tag）" if mode == "characters" else "汉字＋英文单词＋数字（不含标点和空格）"
    print(f"扫描目录：{root.resolve()}")
    print(f"统计口径：{unit_note}")
    total_text = sum(x.text_count for x in files)
    total_names = sum(x.name_count for x in files)
    print(f"全部剧本：{total:,} 字（正文 {total_text:,} + 角色名 {total_names:,}）  |  台词/旁白 {sum(x.say_count for x in files):,} 条  |  选项 {sum(x.menu_count for x in files):,} 条")

    dir_totals = directory_totals(files, root)
    groups: dict[Path, list[FileStats]] = defaultdict(list)
    for item in files:
        groups[item.path.relative_to(root).parent].append(item)

    for directory in sorted(groups, key=lambda p: p.as_posix().lower()):
        print()
        if directory == Path("."):
            print("[根目录文件]")
        else:
            print(f"[目录] {relative_display(directory)}：{dir_totals[directory]:,} 字")
        for item in sorted(groups[directory], key=lambda x: x.path.name.lower()):
            print(f"  {item.path.name}：{item.count:,} 字（正文 {item.text_count:,} + 角色名 {item.name_count:,}）  |  台词/旁白 {item.say_count:,}  |  选项 {item.menu_count:,}")
            # for label in item.labels:
            #     print(f"    label {label.name}：{label.count:,} 字（正文 {label.text_count:,} + 角色名 {label.name_count:,}）  |  台词/旁白 {label.say_count:,}  |  选项 {label.menu_count:,}")

    # Also show parent directory rollups when nested directories exist.
    leaf_dirs = set(groups)
    parents = [p for p in dir_totals if p not in leaf_dirs]
    if parents:
        print("\n[上级目录汇总]")
        for directory in sorted(parents, key=lambda p: (len(p.parts), p.as_posix().lower())):
            print(f"  {relative_display(directory)}：{dir_totals[directory]:,} 字")


def write_csv(path: Path, files: list[FileStats], root: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["目录", "文件", "Label", "总字数", "正文字数", "角色名字数", "台词/旁白条数", "菜单选项条数"])
        for item in files:
            relative = item.path.relative_to(root)
            directory = "" if relative.parent == Path(".") else relative.parent.as_posix()
            for label in item.labels:
                writer.writerow([directory, relative.name, label.name, label.count, label.text_count, label.name_count, label.say_count, label.menu_count])


def resolve_setting(path: Path, script_dir: Path) -> Path:
    return path if path.is_absolute() else script_dir / path


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    root = resolve_setting(SCRIPT_DIRECTORY, script_dir).resolve()
    if not root.is_dir():
        print(f"错误：剧本目录不存在：{root}", file=sys.stderr)
        print("请修改脚本顶部的 SCRIPT_DIRECTORY。", file=sys.stderr)
        return 2
    if COUNT_MODE not in {"characters", "han-words"}:
        print('错误：COUNT_MODE 必须是 "characters" 或 "han-words"。', file=sys.stderr)
        return 2

    character_names: dict[str, str] = {}
    if COUNT_CHARACTER_NAMES and CHARACTER_FILE is not None:
        character_path = resolve_setting(CHARACTER_FILE, script_dir).resolve()
        if not character_path.is_file():
            print(f"错误：Character 定义文件不存在：{character_path}", file=sys.stderr)
            print("请修改脚本顶部的 CHARACTER_FILE，或关闭 COUNT_CHARACTER_NAMES。", file=sys.stderr)
            return 2
        try:
            character_names = load_character_names(character_path)
        except (OSError, ValueError) as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1
        print(f"已读取 Character 定义：{len(character_names):,} 个静态角色名")

    paths = sorted(
        (p for p in root.rglob("*.rpy") if "tl" not in p.relative_to(root).parts),
        key=lambda p: p.as_posix().lower(),
    )
    try:
        files = [parse_file(path, COUNT_MODE, character_names) for path in paths]
    except (OSError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    # Files without labels cannot contain label story content and are omitted.
    files = [item for item in files if item.labels]
    print_report(files, root, COUNT_MODE)
    if CSV_OUTPUT is not None:
        csv_path = resolve_setting(CSV_OUTPUT, script_dir).resolve()
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        write_csv(csv_path, files, root)
        print(f"\nCSV 已写入：{csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
