import csv
import sys
import os
import glob

CHAR_DICT = {
    "时茜": "qian",
    "时茜：": "qian_speaking",
    "黑衣女人": "bfem",
    "黑衣女人：": "bfem_speaking",
    "衬衫女人：": "off_speaking",
    "瘦小女人": "thin_speaking",
    "瘦小女人：": "thin_speaking",
    "瘦小女性：": "thin_speaking",
    "短发女人：": "short_speaking",
    "工作人员": "stf_speaking",
    "工作人员：": "stf_speaking",
    "staff": "stf_speaking",
    "老板：": "boss_speaking",
    "君和：": "jun_speaking",
    "迟玉：": "chi_speaking",
    "莺莺：": "ying_speaking",
    "黎沙：": "li_speaking",
    "？": "unknown",
    "？：": "unknown",
    # place holders start here
    "女人：": "place_holder",
    "同事：": "coworker_speaking",
    "蓝石：": "lan_speaking",
    "白衣女人：": "white_speaking",
    "医生：": "doctor_speaking",
}
JUMP_IDENTIFIER = "Q"
FNAME_IDENTIFIER = "Q"


def get_digits(
    s: str,
):
    return "_".join([ele for ele in s if ele.isdigit()])


def has_digits(
    s: str,
):
    return any(ele.isdigit() for ele in s)


def gen_txt(
    fname: str,
    digits: str,
    output_fname: str = "output.txt",
):
    # Process input file
    data = []
    with open(fname, "r") as file:
        csv_reader = csv.reader(file)

        for row in csv_reader:
            data.append(row)

    # Remove and create a new file with output_fname
    file = open(output_fname, "w")
    file.close()

    # Write to output file output_fname
    # digits = [ele for ele in fname if ele.isdigit()]
    label_name = f"label q{digits}:\n"

    line_counter = 0
    menu_flag = False
    with open(output_fname, "a") as file:
        file.write(label_name)
        for ele in data:
            person, dialog, note = ele[:3]
            line_counter += 1
            # Skip if dialog is empty
            if len(dialog) == 0:
                continue
            # Check if person in CHAR_DICT
            if len(person) > 0 and person not in CHAR_DICT:
                print(
                    f"[ERROR] Undefined character at {fname} row {line_counter} column 1.\n"
                )
            # Character with dialog
            elif person in CHAR_DICT:
                menu_flag = False
                file.write(f'    {CHAR_DICT[person]} "{dialog}"\n')
                # With notes
                if len(note) > 0:
                    file.write(f"    #TODO: {note}\n")
            # Only dialog
            elif len(dialog) > 0 and JUMP_IDENTIFIER not in dialog:
                menu_flag = False
                file.write(f'    "{dialog}"\n')
            # Condition and jump
            else:
                if has_digits(dialog):
                    condition, chapter = dialog.split("Q")
                    if not menu_flag:
                        file.write("    menu:\n")
                        menu_flag = True

                    file.write(f'        "{condition}":\n')
                    file.write(f"            jump q{get_digits(chapter)}\n")
                else:
                    file.write(f"#TODO: {dialog}")

    data.clear()


if __name__ == "__main__":
    assert len(sys.argv) >= 2
    input_file_dir = sys.argv[1]
    input_file_dir = os.path.expanduser(input_file_dir)
    input_file_list = glob.glob(f"{input_file_dir}/*.csv")

    for input_fname in input_file_list:
        print(f"{'*' * 100}")
        print(f"[INFO] Processing {input_fname}")
        assert ".csv" in input_fname and input_fname.count(".csv") == 1
        input_fname_list = input_fname.split(FNAME_IDENTIFIER)
        digits = "_".join([ele for ele in input_fname_list[1] if ele.isdigit()])

        output_dir = os.path.join(os.getcwd(), "game/tmp_scripts")
        output_fname = os.path.join(
            output_dir, f"script_q{digits.replace('_', '-')}.rpy"
        )
        gen_txt(fname=input_fname, digits=digits, output_fname=output_fname)