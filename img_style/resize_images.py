from pathlib import Path
from PIL import Image

input_dir = Path(r"C:\Codes\RPY\VN_DGS\game\images\cg")
output_dir = Path(r"C:\Codes\RPY\VN_DGS\game\images\cg_thumb")
newsize = (256,144)

output_dir.mkdir(parents=True, exist_ok=True)

supported_exts = {".png", ".webp"}

for image_path in input_dir.iterdir():
    if image_path.suffix.lower() not in supported_exts:
        continue

    with Image.open(image_path) as img:
        resized = img.resize(newsize, Image.LANCZOS)

        output_path = output_dir / f"{image_path.stem}_thumb.png"
        resized.save(output_path)


print("Done.")