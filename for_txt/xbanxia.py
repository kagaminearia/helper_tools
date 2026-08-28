# Combine article(1).txt, article(2).txt, ... in numeric order, from xbanxia website
import os
import re

input_folder = r"C:\Codes\helper_tools\for_txt\txt_files"
output_file = os.path.join(input_folder, "combined.txt")

def get_article_number(filename):
    match = re.fullmatch(r"article\((\d+)\)\.txt", filename, re.IGNORECASE)

    if match:
        return int(match.group(1))

    # 不符合命名格式的文件排到最后
    return float("inf")

files = [
    filename
    for filename in os.listdir(input_folder)
    if re.fullmatch(r"article\(\d+\)\.txt", filename, re.IGNORECASE)
]

# 按括号中的数字排序，而不是按字符串排序
files.sort(key=get_article_number)

with open(output_file, "w", encoding="utf-8") as outfile:
    for filename in files:
        file_path = os.path.join(input_folder, filename)

        with open(file_path, "r", encoding="utf-8") as infile:
            outfile.write(infile.read())
            outfile.write("\n\n")

        print(f"Added: {filename}")

print(f"Files combined successfully: {output_file}")