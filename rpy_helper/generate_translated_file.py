import re
import sys


def build_translation_map(reference_path):
    """
    Build a mapping from Chinese text to English translation.
    Only the first occurrence is stored if duplicates exist.
    Supports:
      - # "Chinese" + next line
      - old "Chinese" + next new "English"
    """
    translation_map = {}

    comment_pattern = re.compile(r'#.*?"(.*?)"')
    translation_pattern = re.compile(r'^[^#].*?"(.*?)"')

    old_pattern = re.compile(r'^\s*old\s+"(.*?)"')
    new_pattern = re.compile(r'^\s*new\s+"(.*?)"')

    with open(reference_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines) - 1:
        line = lines[i]

        # ----- Case 1: comment style -----
        comment_match = comment_pattern.search(line)
        if comment_match:
            chinese = comment_match.group(1)
            next_line = lines[i + 1]
            trans_match = translation_pattern.search(next_line)

            if trans_match:
                english = trans_match.group(1)
                if chinese not in translation_map:
                    translation_map[chinese] = english

        # ----- Case 2: old/new style -----
        old_match = old_pattern.match(line)
        if old_match and i + 1 < len(lines):
            chinese = old_match.group(1)
            next_line = lines[i + 1]
            new_match = new_pattern.match(next_line)

            if new_match:
                english = new_match.group(1)
                if chinese not in translation_map:
                    translation_map[chinese] = english

        i += 1

    return translation_map


def fill_translations(reference_path, target_path, output_path):
    translation_map = build_translation_map(reference_path)

    comment_pattern = re.compile(r'#.*?"(.*?)"')
    translation_line_pattern = re.compile(r'^([^#].*?)"(.*?)"(.*)$')

    old_pattern = re.compile(r'^(\s*)old\s+"(.*?)"(.*)$')
    new_pattern = re.compile(r'^(\s*)new\s+"(.*?)"(.*)$')

    with open(target_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # ===============================
        # Case 1: comment + translation
        # ===============================
        comment_match = comment_pattern.search(line)

        if comment_match and i + 1 < len(lines):
            chinese = comment_match.group(1)
            next_line = lines[i + 1]
            trans_match = translation_line_pattern.match(next_line)

            if trans_match:
                prefix, existing, suffix = trans_match.groups()

                if existing.strip():
                    output_lines.append(line)
                    output_lines.append(next_line)
                else:
                    if chinese in translation_map:
                        new_line = f'{prefix}"{translation_map[chinese]}"{suffix}\n'
                    else:
                        new_line = f'{prefix}""{suffix} # TODO-TRANSLATE THIS\n'

                    output_lines.append(line)
                    output_lines.append(new_line)

                i += 2
                continue

        # ===============================
        # Case 2: old/new block
        # ===============================
        old_match = old_pattern.match(line)

        if old_match and i + 1 < len(lines):
            indent, chinese, old_suffix = old_match.groups()
            next_line = lines[i + 1]
            new_match = new_pattern.match(next_line)

            if new_match:
                new_indent, existing, new_suffix = new_match.groups()

                # If already translated → do nothing
                if existing.strip():
                    output_lines.append(line)
                    output_lines.append(next_line)
                else:
                    if chinese in translation_map:
                        new_line = f'{new_indent}new "{translation_map[chinese]}"{new_suffix}\n'
                    else:
                        new_line = f'{new_indent}new ""{new_suffix} #TODO-TRANSLATE THIS\n'

                    output_lines.append(line)
                    output_lines.append(new_line)

                i += 2
                continue

        output_lines.append(line)
        i += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)

refer = "input.rpy"
target = "theCurrent.rpy"
output = "output.rpy"
fill_translations(refer, target, output)

# if __name__ == "__main__":
#     if len(sys.argv) != 4:
#         print(
#             "Usage: \n"
#             "python3 generate_translated_file.py reference.rpy target.rpy output.rpy"
#         )
#         sys.exit(1)

#     fill_translations(sys.argv[1], sys.argv[2], sys.argv[3])
