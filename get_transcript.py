import re

input_file = "input.txt"
output_file = "output.txt"

# matches: 12:20;  1:22:33
timestamp_pattern = re.compile(r'^\d{1,2}:\d{2}(:\d{2})?$')

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

cleaned_lines = []

for line in lines:
    line = line.strip()
    # skip timestamp lines and empty lines
    if not timestamp_pattern.match(line) and line:
        cleaned_lines.append(line)

result = "\n".join(cleaned_lines)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(result)

print("Done!")