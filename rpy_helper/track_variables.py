from pathlib import Path
import re
from collections import defaultdict

def track_variables(folder, variables, extensions=(".rpy")):
    folder = Path(folder)
    variables = set(variables)

    # 记录：
    # per_file[file][var] = [delta1, delta2, ...]
    per_file = defaultdict(lambda: defaultdict(list))
    total_count = defaultdict(int)
    total_delta = defaultdict(int)

    # 匹配： XS += 1; $ YR -= 2; YS = YS + 1
    simple_pattern = re.compile(
        r"\$?\s*\b([A-Za-z_]\w*)\s*(\+=|-=)\s*(-?\d+)"
    )

    expanded_pattern = re.compile(
        r"\$?\s*\b([A-Za-z_]\w*)\s*=\s*\1\s*([+-])\s*(\d+)"
    )

    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")

        for var, op, value in simple_pattern.findall(text):
            if var not in variables:
                continue

            value = int(value)
            delta = value if op == "+=" else -value

            per_file[path.name][var].append(delta)
            total_count[var] += 1
            total_delta[var] += delta

        for var, op, value in expanded_pattern.findall(text):
            if var not in variables:
                continue

            value = int(value)
            delta = value if op == "+" else -value

            per_file[path.name][var].append(delta)
            total_count[var] += 1
            total_delta[var] += delta

    # 输出每个文件
    for filename, vars_found in per_file.items():
        parts = []
        for var in variables:
            if var not in vars_found:
                continue
            changes = vars_found[var]
            formatted = ", ".join(
                f"{var} {'+=' if x >= 0 else '-='} {abs(x)}"
                for x in changes
            )

            parts.append(formatted)

        print(f"{filename}: " + ", ".join(parts))

    print("\nTotal:")
    for var in variables:
        print(
            f"{var}: {total_count[var]} 次, "
            f"数值 {total_delta[var]:+d}"
        )


if __name__ == "__main__":
    track_variables(
        folder = r"C:\Codes\RPY\VN_HerWitch\game\scripts",
        variables = ["XS", "XR", "YS", "YR","end0_pt"],
    )