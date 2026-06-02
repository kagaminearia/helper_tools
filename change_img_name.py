import os
import uuid

folder_path = "C:/ACGN/tempimage"   # 修改成你的文件夹路径

for filename in os.listdir(folder_path):
    old_path = os.path.join(folder_path, filename)

    if os.path.isdir(old_path):
        continue

    ext = os.path.splitext(filename)[1]

    new_name = f"{uuid.uuid4().hex}{ext}"
    new_path = os.path.join(folder_path, new_name)

    os.rename(old_path, new_path)


