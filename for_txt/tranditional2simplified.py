from pathlib import Path
from opencc import OpenCC

input_folder = r"C:\Codes\helper_tools\for_txt\txt_files"
output_folder = r"C:\Codes\helper_tools\for_txt"

def convert_txt_folder(
    input_folder: str,
    output_folder: str | None = None,
    recursive: bool = False,
) -> None:
    """
    将指定文件夹内的所有 .txt 文件从繁体中文转换为简体中文。
    Args:
        input_folder: 输入文件夹路径。
        output_folder:
            输出文件夹路径。
            - None：直接覆盖原文件。
            - 指定路径：转换后的文件保存到该文件夹。
        recursive: 是否处理所有子文件夹。
    """
    source_dir = Path(input_folder)

    if not source_dir.is_dir():
        raise ValueError(f"文件夹不存在：{source_dir}")

    converter = OpenCC("t2s")
    txt_files = source_dir.rglob("*.txt") if recursive else source_dir.glob("*.txt")

    converted_count = 0

    for source_file in txt_files:
        try:
            content = source_file.read_text(encoding="utf-8")
            converted_content = converter.convert(content)

            if output_folder is None:
                destination_file = source_file
            else:
                relative_path = source_file.relative_to(source_dir)
                destination_file = Path(output_folder) / relative_path
                destination_file.parent.mkdir(parents=True, exist_ok=True)

            destination_file.write_text(converted_content, encoding="utf-8")

            converted_count += 1
            print(f"已转换：{source_file} -> {destination_file}")

        except UnicodeDecodeError:
            print(f"跳过非 UTF-8 文件：{source_file}")
        except OSError as error:
            print(f"处理失败：{source_file}，原因：{error}")

    print(f"转换完成，共处理 {converted_count} 个 TXT 文件。")

convert_txt_folder(input_folder,output_folder,False)