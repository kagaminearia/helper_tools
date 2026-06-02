import pandas as pd

# Read Excel file
excel_file_path = 'spirits.xlsx'  # Replace with your Excel file path
data = pd.read_excel(excel_file_path)

# Open a text file to write the formatted lines
output_file_path = 'formatted_output.txt'  # Replace with your desired output file path
with open(output_file_path, 'w') as file:
    # Iterate through DataFrame and write formatted lines to the text file
    for index, row in data.iterrows():
        formatted_line = f"【{row[0]}】{row[1]}\n"
        file.write(formatted_line)

print(f"Formatted lines have been written to '{output_file_path}'")

