import re
import os
import glob

def convert_script(input_file, output_file, char_dict):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Prepare the output lines
    converted_lines = []

    for line in lines:
        # Remove leading/trailing whitespace
        line = line.strip()
        if not line:
            # Skip empty lines
            continue

        # Match lines with 【tag】 format
        match = re.match(r"【(.*?)】(.*)", line)
        if match:
            tag, content = match.groups()
            if tag in char_dict:
                converted_lines.append(f'{char_dict[tag]} "{content.strip()}"')
            else:
                converted_lines.append(f'# {line}')
        else:
            # Lines without 【tag】 are treated as plain text
            # default name tag
            # use 'na' before content
            converted_lines.append(f'nay "{line}"')

    # Write the output to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(converted_lines))

# Example usage
CHAR_DICT = {
    "眠": "xwm",
    "月": "yy",
    "女": "undergrad",
    "保": "security",
    "男": "vendor",
    "编": "editor",
    "妈": "mom",
    "？": "unknown"
}

input_file = "HW_c1-1.md"
output_file = "c1-1.txt"
# convert_script(input_file, output_file, CHAR_DICT)

for md_file in glob.glob("*.md"):
    # Get filename without extension
    base_name = os.path.splitext(md_file)[0]
    # Create output filename
    txt_file = f"{base_name}.txt"
    convert_script(md_file, txt_file, CHAR_DICT)
    print(f"Converted: {md_file} → {txt_file}")
