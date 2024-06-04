import os
import re
import argparse

def load_substitutions(file_path):
    substitutions = {}
    with open(file_path, 'r') as file:
        for line in file:
            if ':' in line:
                misspelled, correct = line.strip().split(':')
                substitutions[misspelled.strip()] = correct.strip()
    return substitutions

def process_file(file_path, substitutions, dry_run):
    excl = ["substitutions.txt", "spell.py", "project-words.txt"]
    if any(file_path.endswith(s) for s in excl):
        #print("SKIP", file_path)
        return
    with open(file_path, 'r') as file:
        lines = file.readlines()
    modified = False
    for i, line in enumerate(lines):
        for misspelled, correct in substitutions.items():
            pattern = re.compile(r'\b{}\b'.format(re.escape(misspelled)))
            if re.search(pattern, line):
                if dry_run:
                    new_line = pattern.sub(correct, line)
                    if new_line != line:
                        modified = True
                        print(f"FOUND '{misspelled}:{correct}' {line.strip()} in {file_path} (line {i+1}): ")
                else:
                    new_line = pattern.sub(correct, line)
                    if new_line != line:
                        lines[i] = new_line
                        modified = True
                        print(f"REPLACED '{misspelled}:{correct}' {new_line.strip()} in {file_path} (line {i+1}): ")
    if modified:
        if not dry_run:
            print(f"will save {file_path}")
            with open(file_path, 'w') as file:
                file.writelines(lines)

def process_directory(directory, substitutions, dry_run):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                process_file(file_path, substitutions, dry_run)
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")
                continue

def main():
    parser = argparse.ArgumentParser(description="Replace misspelled words in files recursively.")
    parser.add_argument("substitutions_file", help="Path to the file containing misspellings and their corrections.")
    parser.add_argument("directories", nargs='+', help="Directories to search for files to process.")
    parser.add_argument("--dry-run", action="store_true", help="If set, just print the lines that would be replaced.")
    
    args = parser.parse_args()

    substitutions = load_substitutions(args.substitutions_file)

    for directory in args.directories:
        process_directory(directory, substitutions, args.dry_run)

if __name__ == "__main__":
    main()
