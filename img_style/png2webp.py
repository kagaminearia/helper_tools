# 批量将 PNG 文件转换为 WebP 文件，无损
from pathlib import Path
from PIL import Image

input_folder = Path(r"C:\Codes\RPY\VN_HerWitch\game\images")

for png_file in input_folder.rglob("*.png"):
    webp_file = png_file.with_suffix(".webp")
    with Image.open(png_file) as image:
        image.save(
            webp_file,
            "WEBP",
            lossless=True,
            method=6
        )

    print(f"Converted: {png_file} -> {webp_file}")

print("====== ALL DONE ======\n")