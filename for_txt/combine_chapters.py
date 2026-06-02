# combine txt files in a folder into one file
import os

input_folder = r"C:\Codes\helper_tools\for_txt\txt_files"
output_file = "combined.txt"

# for "1-13" and "14", different cases
def get_start_chapter(filename):
    name = os.path.splitext(filename)[0]  # remove .txt
    if "-" in name:
        return int(name.split("-")[0])
    else:
        return int(name)

files = [f for f in os.listdir(input_folder) if f.endswith(".txt")]

# Sort by starting chapter
files.sort(key=get_start_chapter)

with open(output_file, "w", encoding="utf-8") as outfile:
    for filename in files:
        with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as infile:
            outfile.write(infile.read())
            outfile.write("\n\n")

print("Files combined successfully.")