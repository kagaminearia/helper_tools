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
            # use 'na' before content
            converted_lines.append(f'na "{line}"')

    # Write the output to a new file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(converted_lines))

# Example usage
CHAR_DICT = {
    "潮": "sc",
    "妈": "scm",
    "澄": "xc",
    "沐":"ym",
    "栖":"lq",
    "浩":"szh",
    "方":"fc",
    "？":"unknown"
}

input_file = "c0_1.md"
output_file = "c0_1.txt"
# convert_script(input_file, output_file, CHAR_DICT)

for md_file in glob.glob("*.md"):
    # Get filename without extension
    base_name = os.path.splitext(md_file)[0]
    # Create output filename
    txt_file = f"{base_name}.txt"
    convert_script(md_file, txt_file, CHAR_DICT)
    print(f"Converted: {md_file} → {txt_file}")
