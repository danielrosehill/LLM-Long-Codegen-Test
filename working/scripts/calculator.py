import os
import csv
import re

# Hardcoded paths
source_folder = "/home/daniel/Git/llm-long-codegen-test/app/data/outputs/prompt1-outputs"
report_file = "/home/daniel/Git/llm-long-codegen-test/app/report.csv"

# Ensure the report directory exists
os.makedirs(os.path.dirname(report_file), exist_ok=True)

# Check if the source folder exists
if not os.path.exists(source_folder):
    print(f"Source folder '{source_folder}' does not exist. Please check the path.")
else:
    # Process markdown files and update the CSV
    with open(report_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(["file-name", "description", "character-count", "code-character-count", "code-percentage", "number-of-code-blocks"])

        for filename in os.listdir(source_folder):
            if filename.endswith(".md"):
                file_path = os.path.join(source_folder, filename)
                file_name_without_suffix = os.path.splitext(filename)[0]

                # Read the first line for description and count characters in the file
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    first_line = content.split('\n')[0].strip()
                    if first_line.startswith("#"):
                        description = first_line[1:].strip()
                    else:
                        description = first_line.strip()

                    # Count total characters
                    char_count = len(content)

                    # Find all code blocks and count their characters and number of blocks
                    code_blocks = re.findall(r"```(.*?)```", content, re.DOTALL)
                    code_char_count = sum(len(code) for code in code_blocks)
                    num_code_blocks = len(code_blocks)

                    # Calculate code percentage
                    code_percentage = (code_char_count / char_count) * 100 if char_count > 0 else 0

                # Write to CSV
                writer.writerow([file_name_without_suffix, description, char_count, code_char_count, f"{code_percentage:.2f}", num_code_blocks])

    print(f"Report generated and saved to {report_file}")