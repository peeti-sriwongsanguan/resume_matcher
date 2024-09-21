import os
import sys
import json

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.resume_parser import parse_resume


def test_resume_parser():
    upload_dir = os.path.join(project_root, 'uploads')

    for filename in os.listdir(upload_dir):
        if filename.lower().endswith(('.pdf', '.docx')):
            file_path = os.path.join(upload_dir, filename)

            print(f"\nProcessing: {filename}")
            print("-" * 50)

            with open(file_path, 'rb') as file:
                result = parse_resume(file, filename)

            print(json.dumps(result, indent=2))
            print("\n")


if __name__ == "__main__":
    test_resume_parser()